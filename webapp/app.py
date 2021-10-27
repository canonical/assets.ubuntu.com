# System
import errno
import flask
import traceback

# Packages
from canonicalwebteam.flask_base.app import FlaskBase
from flask.globals import request
from pilbox.errors import PilboxError
from swiftclient.exceptions import ClientException as SwiftException

# Local
from webapp.commands import token_group
from webapp.database import db_session
from webapp.services import AssetAlreadyExistException, asset_service
from webapp.sso import init_sso, login_required
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
)

app = FlaskBase(
    __name__,
    "assets.ubuntu.com",
    static_folder="../static",
    template_folder="../templates",
)


# Manager routes
# TODO: enable csrf only on the manager view
# csrf = CSRFProtect()
# csrf.init_app(app)

init_sso(app)


@app.route("/manager/")
@login_required
def home():
    query = request.values.get("q", "")
    asset_type = request.values.get("q")

    if query:
        assets = asset_service.find_assets()
        print("assets", list(map(lambda e: e.data, assets)))
    else:
        assets = []

    return flask.render_template(
        "index.html", assets=assets, query=query, type=asset_type
    )


@app.route("/manager/create", methods=["GET", "POST"])
@login_required
def create():
    created_assets = []
    existing_assets = []
    failed_assets = []

    if flask.request.method == "POST":
        tags = flask.request.form.get("tags", "")
        optimize = flask.request.form.get("optimize", True)

        for asset_file in flask.request.files.getlist("assets"):
            try:
                name = asset_file.filename
                content = asset_file.read()

                asset = asset_service.create_asset(
                    file_content=content,
                    friendly_name=name,
                    optimize=optimize,
                    data={"tags": tags},
                )

                created_assets.append(asset)
            except AssetAlreadyExistException as error:
                assets = asset_service.find_assets(query=error)
                if len(assets) > 0:
                    existing_assets.append(*assets)
            except Exception as error:
                failed_assets.append({"file_path": name, "error": str(error)})
                print(traceback.format_exc())
        return flask.render_template(
            "created.html",
            assets=created_assets,
            existing=existing_assets,
            failed=failed_assets,
            tags=tags,
            optimize=optimize,
        )

    return flask.render_template("create.html")


# Error pages
# ===


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def error_handler(error=None):
    code = getattr(error, "code")
    return {"status": code, "message": str(error)}, code


@app.errorhandler(500)
def error_500(error=None):
    app.extensions["sentry"].captureException()
    return {"code": 500, "message": str(error)}, 500


@app.errorhandler(OSError)
def error_os(error=None):
    app.extensions["sentry"].captureException()

    status = 500

    if error.errno in [errno.EPERM, errno.EACCES]:
        status = 403  # Forbidden
    if error.errno in [errno.ENOENT, errno.ENXIO]:
        status = 404  # Not found
    if error.errno in [errno.EEXIST]:
        status = 409  # Conflict
    if error.errno in [errno.E2BIG]:
        status = 413  # Request Entity Too Large

    return {"code": status, "message": error.strerror}, status


@app.errorhandler(PilboxError)
def error_pillbox(error=None):
    app.extensions["sentry"].captureException()

    status = error.status_code
    return (
        {"code": status, "message": f"Pilbox Error: {error.log_message}"},
        500,
    )


@app.errorhandler(SwiftException)
def error_swift(error=None):
    app.extensions["sentry"].captureException()

    status = 500
    if error.http_status > 99:
        status = error.http_status
    elif error.msg[:12] == "Unauthorised":
        # Special case for swiftclient.exceptions.ClientException
        status = 511

    return {"code": status, "message": f"Swift Error: {error.msg}"}, status


# API Routes
# ===

# Assets
app.add_url_rule("/", view_func=get_assets)
app.add_url_rule("/", view_func=create_asset, methods=["POST"])
app.add_url_rule("/<string:file_path>", view_func=get_asset)
app.add_url_rule(
    "/<string:file_path>", view_func=update_asset, methods=["PUT"]
)
app.add_url_rule(
    "/<string:file_path>", view_func=delete_asset, methods=["DELETE"]
)
app.add_url_rule("/<string:file_path>/info", view_func=get_asset_info)

# Tokens
app.add_url_rule("/tokens", view_func=get_tokens)
app.add_url_rule("/tokens/<string:name>", view_func=get_token)
app.add_url_rule(
    "/tokens/<string:name>", view_func=create_token, methods=["POST"]
)
app.add_url_rule(
    "/tokens/<string:name>", view_func=delete_token, methods=["DELETE"]
)

# Redirects
app.add_url_rule("/redirects", view_func=get_redirects)
app.add_url_rule("/redirects", view_func=create_redirect, methods=["POST"])
app.add_url_rule("/redirects/<redirect_path>", view_func=get_redirect)
app.add_url_rule(
    "/redirects/<redirect_path>",
    view_func=update_redirect,
    methods=["PUT"],
)
app.add_url_rule(
    "/redirects/<redirect_path>",
    view_func=delete_redirect,
    methods=["DELETE"],
)

# Teardown
# ===


@app.teardown_appcontext
def remove_db_session(response):
    db_session.remove()
    return response


# CLI commands
# ===
app.cli.add_command(token_group)
