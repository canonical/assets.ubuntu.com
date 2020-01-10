# Standard library
import errno
import uuid
from base64 import b64decode
from datetime import datetime

# Packages
import flask
from wand.image import Image
from pilbox.errors import PilboxError
from swiftclient.exceptions import ClientException as SwiftException

# Local
from webapp.decorators import token_required
from webapp.database import db_session
from webapp.lib.file_helpers import (
    file_error,
    get_mimetype,
    remove_filename_hash,
)
from webapp.lib.http_helpers import error_response, set_headers_for_type
from webapp.lib.processors import ImageProcessor
from webapp.models import Asset, Token
from webapp.swift import file_manager


# Assets
# ===
def _create_asset(
    file_data, friendly_name, tags="", url_path="", optimize=False
):
    data = {"tags": tags}

    if optimize:
        try:
            image = ImageProcessor(file_data)
            image.optimize(allow_svg_errors=True)
            file_data = image.data
            data["optimized"] = True
        except Exception:
            # If optimisation failed, just don't bother optimising
            data["optimized"] = False

    if not url_path:
        url_path = file_manager.generate_asset_path(file_data, friendly_name)

    try:
        with Image(blob=file_data) as image_info:
            data["width"] = image_info.width
            data["height"] = image_info.height
    except Exception:
        # Just don't worry if image reading fails
        pass

    asset = (
        db_session.query(Asset)
        .filter(Asset.file_path == url_path)
        .one_or_none()
    )
    if asset:
        error_message = "Asset already exists at {0}.".format(url_path)

        if "width" not in asset.data and "width" in data:
            asset.data["width"] = data["width"]

        if "height" not in asset.data and "height" in data:
            asset.data["height"] = data["height"]

        db_session.commit()

        raise file_error(
            error_number=errno.EEXIST, message=error_message, filename=url_path
        )

    # Save the file in Swift
    file_manager.create(file_data, url_path)

    # Save file info in Postgres
    asset = Asset(file_path=url_path, data=data, created=datetime.utcnow())
    db_session.add(asset)
    db_session.commit()

    return asset.as_json()


def get_asset(file_path):
    try:
        asset_data = file_manager.fetch(file_path)
        asset_headers = file_manager.headers(file_path)
    except SwiftException as error:
        return error_response(error, file_path)

    def make_datetime(x):
        return datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z")

    last_modified = asset_headers["last-modified"]
    if_modified_since = flask.request.headers.get(
        "HTTP_IF_MODIFIED_SINCE", "Mon, 1 Jan 1980 00:00:00 GMT"
    )

    if make_datetime(last_modified) <= make_datetime(if_modified_since):
        return flask.Response(status=304)

    # Run image processor
    try:
        image = ImageProcessor(asset_data, flask.request.args)
        converted_type = image.process()
        asset_data = image.data
    except (PilboxError, ValueError) as error:
        return error_response(error, file_path)

    # Get a sensible filename, including a converted extension
    filename = remove_filename_hash(file_path)
    if converted_type:
        filename = "{0}.{1}".format(filename, converted_type)

    # Start response, guessing mime type
    response = flask.Response(asset_data, content_type=get_mimetype(filename))

    # Set download filename
    response.headers["Content-Disposition"] = "filename={}".format(filename)
    # Cache all genuine assets forever
    response.headers["Cache-Control"] = "max-age=31556926"
    response.headers["Last-Modified"] = last_modified

    # Set headers base on mime type
    response = set_headers_for_type(response)

    return response


@token_required
def update_asset(file_path):
    asset = (
        db_session.query(Asset)
        .filter(Asset.file_path == file_path)
        .one_or_none()
    )

    if not asset:
        flask.abort(404)

    tags = flask.request.values.get("tags", "")
    asset.data["tags"] = tags

    db_session.commit()

    return flask.jsonify(asset.as_json())


@token_required
def delete_asset(file_path):
    asset = (
        db_session.query(Asset)
        .filter(Asset.file_path == file_path)
        .one_or_none()
    )

    if not asset:
        flask.abort(404)

    try:
        file_manager.delete(file_path)
        db_session.delete(asset)
        db_session.commit()
    except SwiftException as err:
        return error_response(err, file_path)

    return flask.jsonify({"message": "Deleted {0}".format(file_path)})


@token_required
def get_asset_info(file_path):
    """
    Data about an asset
    """
    asset = (
        db_session.query(Asset)
        .filter(Asset.file_path == file_path)
        .one_or_none()
    )

    if not asset:
        flask.abort(404)

    response = flask.jsonify(asset.as_json())
    response.headers["Cache-Control"] = "no-cache"
    return response


@token_required
def get_assets():
    assets = db_session.query(Asset).all()
    return flask.jsonify([asset.as_json() for asset in assets])


@token_required
def create_asset():
    """
    Create a new asset
    """
    tags = flask.request.values.get("tags", "")
    optimize = flask.request.values.get("optimize", False)
    asset = flask.request.values.get("asset")
    friendly_name = flask.request.values.get("friendly-name")
    url_path = flask.request.values.get("url-path", "").strip("/")

    try:
        asset = _create_asset(
            file_data=b64decode(asset),
            friendly_name=friendly_name,
            tags=tags,
            url_path=url_path,
            optimize=optimize,
        )
    except IOError as create_error:
        if create_error.errno == errno.EEXIST:
            return error_response(create_error)
        else:
            raise create_error
    except SwiftException as swift_error:
        return error_response(swift_error, url_path)

    return flask.jsonify(asset), 201


# Tokens
# ===
@token_required
def get_tokens():
    tokens = db_session.query(Token).all()
    return (
        flask.jsonify(
            [{"name": token.name, "token": token.token} for token in tokens]
        ),
        200,
    )


@token_required
def get_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        flask.abort(404)

    return flask.jsonify({"name": token.name, "token": token.token})


@token_required
def create_token(name):
    if not name:
        flask.abort(400, "Missing required field 'name'")

    if db_session.query(Token).filter(Token.name == name).one_or_none():
        flask.abort(400, "A token with this name already exists")

    token = Token(name=name, token=uuid.uuid4().hex)
    db_session.add(token)
    db_session.commit()

    return flask.jsonify({"name": token.name, "token": token.token}), 201


@token_required
def delete_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        flask.abort(404, f"No token named '{name}'")

    db_session.delete(token)
    db_session.commit()

    return flask.jsonify({}), 204
