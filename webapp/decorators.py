import functools

import flask

from webapp.auth import authenticate


def get_token_from_request(request):
    auth_header = request.headers.get("Authorization", "")

    if auth_header[:6].lower() == "token ":
        return auth_header[6:]

    return request.args.get("token", None)


def token_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        token = get_token_from_request(flask.request)
        if not token or not authenticate(token):
            message = "Invalid or missing token."
            flask.abort(401, message)

        return f(*args, **kwargs)

    return wrapped
