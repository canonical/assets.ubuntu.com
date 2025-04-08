# Standard library
import math
import re
import uuid
from datetime import datetime
from distutils.util import strtobool
from os import environ
from urllib.parse import unquote, urlparse

import requests

# Packages
from flask import Response, abort, jsonify, redirect, request

# Local
from webapp.database import db_session
from webapp.decorators import token_required
from webapp.param_parser import parse_asset_search_params
from webapp.sso import login_required
from webapp.lib.file_helpers import get_mimetype, remove_filename_hash
from webapp.lib.http_helpers import set_headers_for_type
from webapp.lib.processors import ImageProcessor
from webapp.models import Asset, Redirect, Token
from webapp.services import (
    AssetAlreadyExistException,
    AssetNotFound,
    asset_service,
)
from webapp.swift import file_manager

# Assets
# ===


def get_asset(file_path: str):
    """
    Get the asset content.
    """

    request_url = urlparse(request.path)
    # remove multiple slashes
    request_path = re.sub("//+", "/", request_url.path)
    # remove /v1 prefix
    request_path = re.sub(r"^\/v1", "", request_path)
    # remove the / from the beginning
    request_path = request_path.lstrip("/")

    redirect_record = (
        db_session.query(Redirect)
        .filter(Redirect.redirect_path == request_path)
        .one_or_none()
    )

    if redirect_record:
        # Cache permanent redirect longtime. Temporary, not so much.
        max_age = (
            "max-age=31556926" if redirect_record.permanent else "max-age=60"
        )
        target_url = redirect_record.target_url + "?" + request_url.query
        response = redirect(target_url)
        response.headers["Cache-Control"] = max_age

        return set_headers_for_type(response, get_mimetype(request_path))

    asset_data = file_manager.fetch(file_path)
    if not asset_data:
        abort(404, f"No asset found for '{file_path}'")

    asset_headers = file_manager.headers(file_path)

    def make_datetime(x):
        return datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z")

    last_modified = asset_headers["last-modified"]
    if_modified_since = request.headers.get(
        "HTTP_IF_MODIFIED_SINCE", "Mon, 1 Jan 1980 00:00:00 GMT"
    )

    if make_datetime(last_modified) <= make_datetime(if_modified_since):
        return jsonify({}), 304

    # Run image processor
    image = ImageProcessor(asset_data, request.args)
    converted_type = image.process()
    asset_data = image.data

    # Get a sensible filename, including a converted extension
    filename = remove_filename_hash(file_path)
    if converted_type:
        filename = f"{filename}.{converted_type}"

    # Start response, guessing mime type
    response = Response(asset_data, content_type=get_mimetype(filename))

    # Set download filename
    response.headers["Content-Disposition"] = f"filename={filename}"
    # Cache all genuine assets forever
    response.headers["Cache-Control"] = "max-age=31556926"
    response.headers["Last-Modified"] = last_modified

    # Set headers base on mime type
    response = set_headers_for_type(response)

    return response


@token_required
def update_asset(file_path):
    tags = request.values.get("tags", "").split(",")
    products = request.values.get("products", "").split(",")
    deprecated = strtobool(request.values.get("deprecated", "false"))
    asset_type = request.values.get("asset-type", "")
    author = request.values.get("author", "")
    google_drive_link = request.values.get("google_drive_link", "")
    salesforce_campaign_id = request.values.get("salesforce_campaign_id", "")
    language = request.values.get("language", "")
    try:
        asset = asset_service.update_asset(
            file_path=file_path,
            tags=tags,
            deprecated=deprecated,
            products=products,
            asset_type=asset_type,
            author=author,
            google_drive_link=google_drive_link,
            salesforce_campaign_id=salesforce_campaign_id,
            language=language,
        )
        return jsonify(asset.as_json())
    except AssetNotFound:
        abort(404)


@token_required
def delete_asset(file_path):
    asset = (
        db_session.query(Asset)
        .filter(Asset.file_path == file_path)
        .one_or_none()
    )

    if not asset:
        abort(404)

    file_manager.delete(file_path)
    db_session.delete(asset)
    db_session.commit()

    return jsonify({"message": f"Deleted {file_path}"})


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
        abort(404)

    response = jsonify(asset.as_json())
    response.headers["Cache-Control"] = "no-cache"
    return response


@token_required
def get_assets():
    """
    Get a list of assets metadata.
    """
    search_params = parse_asset_search_params()

    file_type = request.values.get("type", "")
    page = request.values.get("page", type=int)
    per_page = request.values.get("per_page", type=int)
    include_deprecated = (
        strtobool(request.values.get("include_deprecated", "false")) == 1
    )
    page = 1 if not page or page < 1 else page
    per_page = (
        20 if not per_page or per_page < 1 or per_page > 100 else per_page
    )

    if any(
        [
            search_params.tag,
            search_params.asset_type,
            search_params.author_email,
            search_params.name,
            search_params.start_date,
            search_params.end_date,
            search_params.salesforce_campaign_id,
            search_params.language,
        ]
    ):
        assets, total = asset_service.find_assets(
            tag=search_params.tag,
            asset_type=search_params.asset_type,
            product_types=search_params.product_types,
            author_email=search_params.author_email,
            asset_name=search_params.name,
            start_date=search_params.start_date,
            end_date=search_params.end_date,
            salesforce_campaign_id=search_params.salesforce_campaign_id,
            language=search_params.language,
            file_types=[file_type],
            page=page,
            per_page=per_page,
            include_deprecated=include_deprecated,
        )
    else:
        assets = asset_service.find_all_assets()

    return jsonify(
        {
            "assets": [asset.as_json() for asset in assets],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": math.ceil(total / per_page),
        }
    )


@token_required
def create_asset():
    """
    Create a new asset
    """
    created_assets = []
    existing_assets = []
    failed_assets = []

    if request.method == "POST":
        friendly_name = request.values.get("friendly-name")
        optimize = strtobool(request.values.get("optimize", "false"))
        tags = request.values.get("tags", "").split(",")
        products = request.values.get("products", "").split(",")
        url_path = request.values.get("url-path", "").strip("/")
        asset_type = request.values.get("asset-type", "")
        author = request.values.get("author", "")
        google_drive_link = request.values.get("google_drive_link", "")
        salesforce_campaign_id = request.values.get(
            "salesforce_campaign_id",
            "",
        )
        language = request.values.get("language", "")
        deprecated = (
            request.values.get("deprecated", "false").lower() == "true"
        )

        # Process uploaded files
        try:
            for asset_file in request.files.getlist("assets"):
                asset = asset_service.create_asset(
                    file_content=asset_file.read(),
                    friendly_name=friendly_name,
                    optimize=optimize,
                    tags=tags,
                    products=products,
                    url_path=url_path,
                    asset_type=asset_type,
                    author=author,
                    google_drive_link=google_drive_link,
                    salesforce_campaign_id=salesforce_campaign_id,
                    language=language,
                    deprecated=deprecated,
                )
                created_assets.append(asset)

        except AssetAlreadyExistException as error:
            existing_assets.append(
                {"file_path": friendly_name, "error": str(error)},
            )
            return jsonify(failed_assets), 409
        except Exception as error:
            failed_assets.append(
                {"file_path": friendly_name, "error": str(error)},
            )
            return jsonify(failed_assets), 400

    created_assets = [i.as_json() for i in created_assets]
    return jsonify(created_assets), 201


# Tokens
# ===
@token_required
def get_tokens():
    tokens = db_session.query(Token).all()
    return (
        jsonify(
            [{"name": token.name, "token": token.token} for token in tokens]
        ),
        200,
    )


@token_required
def get_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        abort(404)

    return jsonify({"name": token.name, "token": token.token})


@token_required
def create_token(name):
    if not name:
        abort(400, "Missing required field 'name'")

    if db_session.query(Token).filter(Token.name == name).one_or_none():
        abort(400, "A token with this name already exists")

    token = Token(name=name, token=uuid.uuid4().hex)
    db_session.add(token)
    db_session.commit()

    return jsonify({"name": token.name, "token": token.token}), 201


@token_required
def delete_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        abort(404, f"No token named '{name}'")

    db_session.delete(token)
    db_session.commit()

    return jsonify({}), 204


# Redirects
# ---
@token_required
def get_redirect(redirect_path):
    redirect_record = (
        db_session.query(Redirect)
        .filter(Redirect.redirect_path == redirect_path)
        .one_or_none()
    )

    if not redirect_record:
        abort(404, f"No redirect for '{redirect_path}'")

    return jsonify(redirect_record.as_json())


@token_required
def get_redirects():
    redirect_records = db_session.query(Redirect).all()
    return jsonify(
        [redirect_record.as_json() for redirect_record in redirect_records]
    )


@token_required
def create_redirect():
    """
    Create a redirect record
    """

    redirect_path = request.values.get("redirect_path")
    target_url = request.values.get("target_url")
    permanent = request.values.get("permanent", "false").lower() in (
        "true",
        "yes",
        "on",
    )

    if not redirect_path and target_url:
        abort(
            400,
            "To create a new redirect, please specify a "
            "redirect_path and a target_url",
        )

    redirect_path = re.sub("//+", "/", redirect_path.lstrip("/"))
    redirect_record = (
        db_session.query(Redirect)
        .filter(Redirect.redirect_path == redirect_path)
        .one_or_none()
    )

    if redirect_record:
        return (
            jsonify(
                {
                    "message": (
                        "Another redirect with that path already exists"
                    ),
                    "redirect_path": redirect_path,
                    "code": 409,
                }
            ),
            409,
        )

    redirect_record = Redirect(
        redirect_path=redirect_path, target_url=target_url, permanent=permanent
    )
    redirect_record
    db_session.add(redirect_record)
    db_session.commit()

    return jsonify(redirect_record.as_json()), 201


@token_required
def update_redirect(redirect_path):
    target_url = request.values.get("target_url")
    permanent = request.values.get("permanent", "false").lower() in (
        "true",
        "yes",
        "on",
    )

    redirect_record = (
        db_session.query(Redirect)
        .filter(Redirect.redirect_path == redirect_path)
        .one_or_none()
    )
    if not redirect_record:
        abort(404, f"No redirect for '{redirect_path}'")

    redirect_record.redirect_path = unquote(redirect_path)
    redirect_record.target_url = target_url
    redirect_record.permanent = permanent

    db_session.commit()

    return jsonify(redirect_record.as_json())


@token_required
def delete_redirect(redirect_path):
    redirect_record = (
        db_session.query(Redirect)
        .filter(Redirect.redirect_path == redirect_path)
        .one_or_none()
    )

    if not redirect_record:
        abort(404, f"No redirect for '{redirect_path}'")

    db_session.delete(redirect_record)
    db_session.commit()

    return jsonify({}), 204


@login_required
def get_users(username: str):
    query = """
    query($name: String!) {
        employees(filter: { contains: { name: $name }}) {
            id
            firstName
            surname
            email
            team
            department
            jobTitle
        }
    }
    """

    headers = {"Authorization": "token " + environ.get("DIRECTORY_API_TOKEN")}
    response = requests.post(
        "https://directory.wpe.internal/graphql/",
        json={
            "query": query,
            "variables": {"name": username.strip()},
        },
        headers=headers,
        verify=False,
        timeout=10,
    )

    if response.status_code == 200:
        users = response.json().get("data", {}).get("employees", [])
        return jsonify(list(users))
    return jsonify({"error": "Failed to fetch users"}), 500
