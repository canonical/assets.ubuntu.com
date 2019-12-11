from canonicalwebteam.flask_base.app import FlaskBase

from webapp.alembic.env import get_database_session
from webapp.decorators import token_required
from webapp.tokens.cli import token_cli
from webapp.tokens.flask import tokens_blueprint


app = FlaskBase(__name__, "assets.ubuntu.com")

# Register tokens blueprint and CLI
app.register_blueprint(tokens_blueprint)
app.cli.add_command(token_cli)
database_session = get_database_session()

@app.route("/")
@token_required
def index():
    return {}, 200


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


@app.teardown_appcontext
def remove_db_session(response):
    database_session.remove()
    return response
