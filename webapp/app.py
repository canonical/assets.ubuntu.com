import flask

from canonicalwebteam.flask_base.app import FlaskBase
from webapp.decorators import token_required


app = FlaskBase(__name__, "assets.ubuntu.com")


@app.route("/")
@token_required
def index():
    return {}, 200


@app.errorhandler(401)
def error_401(exception=None):
    return {"status": "401", "message": str(exception)}, 401


@app.errorhandler(404)
def error_404(exception=None):
    return {"status": "404", "message": "Resource not found"}, 404


@app.errorhandler(500)
def error_500(exception=None):
    flask.current_app.extensions["sentry"].captureException()
    return {"status": "500", "message": ""}, 500
