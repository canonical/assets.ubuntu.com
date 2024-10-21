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
from webapp.param_parser import parse_asset_search_params
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
    search_params = parse_asset_search_params()

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
        assets = asset_service.find_assets(
            tag=search_params.tag,
            asset_type=search_params.asset_type,
            product_types=search_params.product_types,
            author_email=search_params.author_email,
            name=search_params.name,
            start_date=search_params.start_date,
            end_date=search_params.end_date,
            salesforce_campaign_id=search_params.salesforce_campaign_id,
            language=search_params.language,
        )
    else:
        assets = []

    return flask.render_template(
        "index.html",
        assets=assets,
        query=search_params.tag,
        type=search_params.asset_type,
    )


@ui_blueprint.route("/create", methods=["POST"])
@login_required
def create():
    created_assets = []
    existing_assets = []
    failed_assets = []

    if flask.request.method == "POST":
        tags = flask.request.form.get("tags", "")
        tags = re.split(",|\\s", tags)
        products = flask.request.form.get("products", "")
        products = re.split(",|\\s", products)
        google_drive_link = flask.request.form.get("google_drive_link", "")
        salesforce_campaign_id = flask.request.form.get(
            "salesforce_campaign_id", ""
        )
        language = flask.request.form.get("language", "")
        deprecated = (
            flask.request.form.get("deprecated", "false").lower() == "true"
        )
        optimize = flask.request.form.get("optimize", True)
        asset_type = flask.request.form.get("asset_type", "")
        author_email = flask.request.form.get("author_email", "")
        author_first_name = flask.request.form.get("author_first_name", "")
        author_last_name = flask.request.form.get("author_last_name", "")
        author = {
            "email": author_email,
            "first_name": author_first_name,
            "last_name": author_last_name,
        }

        for asset_file in flask.request.files.getlist("assets"):
            try:
                name = asset_file.filename
                content = asset_file.read()

                asset = asset_service.create_asset(
                    file_content=content,
                    friendly_name=name,
                    optimize=optimize,
                    tags=tags,
                    products=products,
                    asset_type=asset_type,
                    author=author,
                    google_drive_link=google_drive_link,
                    salesforce_campaign_id=salesforce_campaign_id,
                    language=language,
                    deprecated=deprecated,
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
        tags = request.form.get("tags").split(",")
        products = request.form.get("products", "").split(",")
        deprecated = strtobool(request.form.get("deprecated", "false"))
        asset_type = request.form.get("asset_type", "")
        google_drive_link = request.form.get("google_drive_link", "")
        salesforce_campaign_id = request.form.get("salesforce_campaign_id", "")
        language = request.form.get("language", "")
        author_email = flask.request.form.get("author_email", "")
        author_first_name = flask.request.form.get("author_first_name", "")
        author_last_name = flask.request.form.get("author_last_name", "")
        author = {
            "email": author_email,
            "first_name": author_first_name,
            "last_name": author_last_name,
        }

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
api_blueprint.add_url_rule(
    "/<path:file_path>", view_func=update_asset, methods=["PUT"]
)
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
api_blueprint.add_url_rule(
    "/redirects", view_func=create_redirect, methods=["POST"]
)
api_blueprint.add_url_rule(
    "/redirects/<path:redirect_path>", view_func=get_redirect
)
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
