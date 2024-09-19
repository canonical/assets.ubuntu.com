# System
import re
from distutils.util import strtobool

# Packages
from flask import Blueprint
from flask.globals import request
import flask

# Local
from webapp.services import (
    AssetAlreadyExistException,
    AssetNotFound,
    asset_service,
)
from webapp.sso import login_required
from webapp.views import (
    create_asset,
    create_redirect,
    create_token,
    delete_asset,
    delete_redirect,
    delete_token,
    get_asset,
    get_asset_info,
    get_assets,
    get_redirect,
    get_redirects,
    get_token,
    get_tokens,
    update_asset,
    update_redirect,
    get_users,
)


ui_blueprint = Blueprint("ui_blueprint", __name__, url_prefix="/manager")
api_blueprint = Blueprint("api_blueprint", __name__, url_prefix="/v1")

# Manager Routes
# ===


@ui_blueprint.route("/")
@login_required
def home():
    query = request.values.get("q", "")
    tag = request.values.get("tag", None)
    asset_type = request.values.get("type")

    if query or tag:
        assets = asset_service.find_assets(query=query, file_type=asset_type, tag=tag)
    else:
        assets = []

    return flask.render_template(
        "index.html", assets=assets, query=query, type=asset_type
    )


@ui_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    created_assets = []
    existing_assets = []
    failed_assets = []

    if flask.request.method == "POST":
        tags = flask.request.form.get("tags", "")
        tags = re.split(",|\\s", tags)

        optimize = flask.request.form.get("optimize", True)

        for asset_file in flask.request.files.getlist("assets"):
            try:
                name = asset_file.filename
                content = asset_file.read()

                asset = asset_service.create_asset(
                    file_content=content,
                    friendly_name=name,
                    optimize=optimize,
                    tags=tags,
                )

                created_assets.append(asset)
            except AssetAlreadyExistException as error:
                asset = asset_service.find_asset(str(error))
                if asset:
                    existing_assets.append(asset)
            except Exception as error:
                failed_assets.append({"file_path": name, "error": str(error)})
        return flask.render_template(
            "created.html",
            assets=created_assets,
            existing=existing_assets,
            failed=failed_assets,
            tags=tags,
            optimize=optimize,
        )

    return flask.render_template("create.html")


@ui_blueprint.route("/update", methods=["GET", "POST"])
@login_required
def update():
    file_path = request.args.get("file-path")

    if request.method == "GET":
        asset = asset_service.find_asset(file_path)
        if not asset:
            flask.flash("Asset not found", "negative")

    elif request.method == "POST":
        tags = request.form.get("tags")
        deprecated = strtobool(request.form.get("deprecated", "false"))
        try:
            asset = asset_service.update_asset(
                file_path, tags=tags.split(","), deprecated=deprecated
            )
            flask.flash("Asset updated", "positive")
        except AssetNotFound:
            flask.flash("Asset not found", "negative")

    return flask.render_template("update.html", asset=asset)


# API Routes
# ===

# Assets
api_blueprint.add_url_rule("/", view_func=get_assets)
api_blueprint.add_url_rule("/", view_func=create_asset, methods=["POST"])
api_blueprint.add_url_rule("/<path:file_path>", view_func=get_asset)
api_blueprint.add_url_rule("/<path:file_path>", view_func=update_asset, methods=["PUT"])
api_blueprint.add_url_rule(
    "/<path:file_path>", view_func=delete_asset, methods=["DELETE"]
)
api_blueprint.add_url_rule("/<path:file_path>/info", view_func=get_asset_info)

# Tokens
api_blueprint.add_url_rule("/tokens", view_func=get_tokens)
api_blueprint.add_url_rule("/tokens/<string:name>", view_func=get_token)
api_blueprint.add_url_rule(
    "/tokens/<string:name>", view_func=create_token, methods=["POST"]
)
api_blueprint.add_url_rule(
    "/tokens/<string:name>", view_func=delete_token, methods=["DELETE"]
)

# Redirects
api_blueprint.add_url_rule("/redirects", view_func=get_redirects)
api_blueprint.add_url_rule("/redirects", view_func=create_redirect, methods=["POST"])
api_blueprint.add_url_rule("/redirects/<path:redirect_path>", view_func=get_redirect)
api_blueprint.add_url_rule(
    "/redirects/<path:redirect_path>",
    view_func=update_redirect,
    methods=["PUT"],
)
api_blueprint.add_url_rule(
    "/redirects/<path:redirect_path>",
    view_func=delete_redirect,
    methods=["DELETE"],
)
api_blueprint.add_url_rule(
    "/get-users/<username>",
    view_func=get_users,
    methods=["GET"],
)
