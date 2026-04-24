import functools
import os
from urllib.parse import urljoin, urlparse

import flask
from authlib.integrations.flask_client import OAuth


def is_safe_url(target):
    if not target:
        return False

    # Security: Prevent "///" or "\\\" bypasses
    # that some browsers interpret as absolute URLs
    if target.startswith(("\\", "//")):
        return False

    ref_url = urlparse(flask.request.host_url)
    test_url = urlparse(urljoin(flask.request.host_url, target))

    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
    )


def _safe_redirect():
    # .get() returns None if missing, which is_safe_url handles
    target = flask.request.args.get("next")

    if not is_safe_url(target):
        return flask.redirect("/manager")

    return flask.redirect(target)


def init_sso(app):

    oauth = OAuth(app)

    oauth.register(
        "canonical",
        client_id=os.getenv("SSO_CLIENT_ID"),
        client_secret=os.getenv("SSO_CLIENT_SECRET"),
        server_metadata_url=os.getenv("SSO_PROVIDER"),
        client_kwargs={
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid profile email",
        },
    )

    @app.route("/login")
    def login():
        if "openid" in flask.session:
            return _safe_redirect()

        redirect_uri = flask.url_for("oauth_callback", _external=True)
        return oauth.canonical.authorize_redirect(redirect_uri)

    @app.route("/auth/callback")
    def oauth_callback():
        token = oauth.canonical.authorize_access_token()
        user_email = token["userinfo"]["email"]
        if not user_email.endswith("@canonical.com"):
          flask.abort(403, description="Canonical employees only")
        flask.session["openid"] = {
            "identity_url": token["userinfo"]["iss"],
            "email": token["userinfo"]["email"],
            "fullname": token["userinfo"]["name"],
        }
        return _safe_redirect()


def login_required(func):
    """
    Decorator that checks if a user is logged in, and redirects
    to login page if not.
    """

    @functools.wraps(func)
    def is_user_logged_in(*args, **kwargs):
        disable_auth = str(
            os.getenv("FLASK_DISABLE_AUTH_FOR_TESTS", "")
        ).lower() in (
            "1",
            "true",
        )
        if disable_auth:
            return func(*args, **kwargs)

        if "openid" not in flask.session:
            return flask.redirect("/login?next=" + flask.request.path)
        response = flask.make_response(func(*args, **kwargs))
        response.cache_control.private = True
        return response

    return is_user_logged_in
