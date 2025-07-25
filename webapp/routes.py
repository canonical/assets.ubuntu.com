# System
import math
import re
from distutils.util import strtobool
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Packages
import flask
import yaml
from flask import Blueprint
from flask.globals import request

# Local
from webapp.param_parser import parse_asset_search_params
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
    get_users,
    update_asset,
    update_redirect,
)

ui_blueprint = Blueprint("ui_blueprint", __name__, url_prefix="/manager")
api_blueprint = Blueprint("api_blueprint", __name__, url_prefix="/v1")

with open("form-field-data.yaml") as file:
    form_field_data = yaml.load(file, Loader=yaml.FullLoader)

# Manager Routes
# ===


def add_query_param(key, value):
    """
    A jinja helper to upsert query parameter in the URL
    """
    url = request.url
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query[key] = value
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


ui_blueprint.add_app_template_global(
    add_query_param,
    "add_query_param",
)


@ui_blueprint.route("/", methods=["GET"])
@login_required
def home():
    search_params = parse_asset_search_params()

    page = request.values.get("page", type=int, default=1)
    per_page = request.values.get("per_page", type=int)
    order_by = request.values.get("order_by", type=str)
    order_dir = request.values.get("order_dir", type=str, default="desc")
    include_deprecated = request.values.get(
        "include_deprecated", type=bool, default=False
    )

    if not per_page or per_page < 1 or per_page > 100:
        per_page = 16
    if order_by not in asset_service.order_by_fields():
        order_by = list(asset_service.order_by_fields().keys())[0]
    if order_dir not in ["asc", "desc"]:
        order_dir = "desc"

    assets = []
    total = 0
    is_search = False
    if any(
        [
            search_params.tag,
            search_params.asset_type,
            search_params.product_types,
            search_params.author_email,
            search_params.start_date,
            search_params.end_date,
            search_params.salesforce_campaign_id,
            search_params.language,
            search_params.file_types,
        ]
    ):
        assets, total = asset_service.find_assets(
            tag=search_params.tag,
            asset_type=search_params.asset_type,
            product_types=search_params.product_types,
            author_email=search_params.author_email,
            start_date=search_params.start_date,
            end_date=search_params.end_date,
            salesforce_campaign_id=search_params.salesforce_campaign_id,
            language=search_params.language,
            page=page,
            per_page=per_page,
            order_by=asset_service.order_by_fields()[order_by],
            desc_order=order_dir == "desc",
            include_deprecated=include_deprecated,
            file_types=search_params.file_types,
        )
        is_search = True

    return flask.render_template(
        "index.html",
        assets=assets,
        available_extensions=asset_service.available_extensions(),
        assets_count=len(assets),
        total_assets=total,
        page=page,
        total_pages=math.ceil(total / per_page),
        per_page=per_page,
        type=search_params.asset_type,
        order_by=order_by,
        order_dir=order_dir,
        order_by_fields=asset_service.order_by_fields(),
        include_deprecated=include_deprecated,
        query=search_params.tag,
        form_field_data=form_field_data,
        is_search=is_search,
    )


@ui_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    created_assets = []
    existing_assets = []
    failed_assets = []

    if request.method == "POST":
        form_data = {
            "tags": request.form.get("tags", ""),
            "products": request.form.get("products", ""),
            "google_drive_link": request.form.get("google_drive_link", ""),
            "salesforce_campaign_id": request.form.get(
                "salesforce_campaign_id", ""
            ),
            "language": request.form.get("language", "") or "English",
            "deprecated": request.form.get("deprecated", "false").lower()
            == "true",
            "asset_type": request.form.get("asset_type", "") or "image",
            "author_email": request.form.get("author_email", ""),
            "author_first_name": request.form.get("author_first_name", ""),
            "author_last_name": request.form.get("author_last_name", ""),
            "name": request.form.get("name", ""),
        }
        form_data["tags"] = re.split(",|\\s", form_data["tags"])
        form_data["products"] = re.split(",|\\s", form_data["products"])
        author = {
            "email": form_data["author_email"],
            "first_name": form_data["author_first_name"],
            "last_name": form_data["author_last_name"],
        }
        optimize = request.form.get("optimize", True)

        # Save to session
        flask.session["form_data"] = form_data

        # Process uploaded files
        for asset_file in request.files.getlist("assets"):
            try:
                filename = asset_file.filename
                content = asset_file.read()

                asset = asset_service.create_asset(
                    file_content=content,
                    friendly_name=filename,
                    name=form_data["name"],
                    optimize=optimize,
                    tags=form_data["tags"],
                    products=form_data["products"],
                    asset_type=form_data["asset_type"],
                    author=author,
                    google_drive_link=form_data["google_drive_link"],
                    salesforce_campaign_id=form_data["salesforce_campaign_id"],
                    language=form_data["language"],
                    deprecated=form_data["deprecated"],
                )

                created_assets.append(asset)
            except AssetAlreadyExistException as error:
                asset = asset_service.find_asset(str(error))
                if asset:
                    existing_assets.append(asset)
            except Exception as error:
                failed_assets.append(
                    {"file_path": filename, "error": str(error)}
                )

        # If submission was successful, clear session
        if not existing_assets and not failed_assets:
            flask.session.pop("form_data", None)

        return flask.render_template(
            "created.html",
            assets=created_assets,
            existing=existing_assets,
            failed=failed_assets,
            tags=form_data["tags"],
            optimize=optimize,
        )

    if request.method == "GET":
        # Repopulate the form with stored data
        form_data = flask.session.pop("form_data", {})
        return flask.render_template(
            "create-update.html",
            form_field_data=form_field_data,
            form_session_data=form_data,
        )


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
        author_email = request.form.get("author_email", "")
        author_first_name = request.form.get("author_first_name", "")
        author_last_name = request.form.get("author_last_name", "")
        author = {
            "email": author_email,
            "first_name": author_first_name,
            "last_name": author_last_name,
        }
        name = request.form.get("name", "")
        try:
            asset = asset_service.update_asset(
                file_path=file_path,
                tags=tags,
                name=name,
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
        return flask.redirect("/manager/details?file-path=" + file_path)

    return flask.render_template(
        "create-update.html", form_field_data=form_field_data, asset=asset
    )


@ui_blueprint.route("/details", methods=["GET"])
@login_required
def details():
    file_path = request.args.get("file-path")

    asset = asset_service.find_asset(file_path)
    if not asset:
        flask.flash("Asset not found", "negative")

    return flask.render_template("details.html", asset=asset)


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
