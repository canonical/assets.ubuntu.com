# System
import errno
import http.client

# Packages
from canonicalwebteam.flask_base.app import FlaskBase
from flask_wtf.csrf import CSRFProtect
from flask.globals import request
from pilbox.errors import PilboxError
from swiftclient.exceptions import ClientException as SwiftException
import flask


# Local
from webapp.commands import db_group, token_group
from webapp.database import db_session
from webapp.routes import api_blueprint, ui_blueprint
from webapp.sso import init_sso

app = FlaskBase(
    __name__,
    "assets.ubuntu.com",
    static_folder="../static",
    template_folder="../templates",
)


csrf = CSRFProtect()
csrf.init_app(app)
csrf.exempt(api_blueprint)
init_sso(app)


# Error pages
# ===
def render_error(code, message):
    # return JSON format in case of api route (with prefix /v1)
    if request.full_path.startswith(api_blueprint.url_prefix + "/"):
        return {"code": code, "message": message}, code
    else:
        return (
            flask.render_template(
                "error.html",
                code=code,
                reason=http.client.responses.get(code),
                message=message,
            ),
            code,
        )


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def error_handler(error=None):
    code = getattr(error, "code")
    return render_error(code, str(error))


@app.errorhandler(500)
def error_500(error=None):
    app.extensions["sentry"].captureException()
    return render_error(500, str(error))


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

    return render_error(status, str(error.strerror))


@app.errorhandler(PilboxError)
def error_pillbox(error=None):
    app.extensions["sentry"].captureException()

    status = error.status_code
    return render_error(status, f"Pilbox Error: {error.log_message}")


@app.errorhandler(SwiftException)
def error_swift(error=None):
    app.extensions["sentry"].captureException()

    status = 500
    if error.http_status > 99:
        status = error.http_status
    elif error.msg[:12] == "Unauthorised":
        # Special case for swiftclient.exceptions.ClientException
        status = 511
    return render_error(status, f"Swift Error: {error.msg}")


# Apply blueprints
# ===
app.register_blueprint(ui_blueprint)
app.register_blueprint(api_blueprint)

# Teardown
# ===


@app.teardown_appcontext
def remove_db_session(response):
    db_session.remove()
    return response


# CLI commands
# ===
app.cli.add_command(token_group)
app.cli.add_command(db_group)
