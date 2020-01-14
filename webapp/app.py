# Packages
from canonicalwebteam.flask_base.app import FlaskBase

# Local
from webapp.views import (
    create_asset,
    create_token,
    delete_asset,
    delete_token,
    get_asset,
    get_assets,
    get_asset_info,
    get_tokens,
    get_token,
    update_asset,
)
from webapp.database import db_session
from webapp.commands import token_group


app = FlaskBase(__name__, "assets.ubuntu.com")


# Error pages
# ===


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def error_handler(exception=None):
    code = getattr(exception, "code")
    return {"status": f"{code}", "message": str(exception)}, code


@app.errorhandler(500)
def error_500(exception=None):
    app.extensions["sentry"].captureException()
    return {"status": "500", "message": ""}, 500


# Routes
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


# Teardown
# ===
@app.teardown_appcontext
def remove_db_session(response):
    db_session.remove()
    return response


# CLI commands
# ===
app.cli.add_command(token_group)
