# Standard library
import functools

# Packages
import flask

# Local
from webapp.auth import authenticate


def get_token_from_request(request):
    auth_header = request.headers.get("Authorization", "")

    if auth_header[:6].lower() == "token ":
        return auth_header[6:]

    return request.values.get("token", None)


def token_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        token = get_token_from_request(flask.request)
        if not token or not authenticate(token):
            message = "Invalid or missing token."
            flask.abort(401, message)

        response = flask.make_response(f(*args, **kwargs))
        response.cache_control.private = True

        return response

    return wrapped
