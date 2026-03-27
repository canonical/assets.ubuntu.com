import functools
import os
from urllib.parse import urlparse

import flask
from authlib.integrations.flask_client import OAuth
import requests

from webapp.views import get_users_data

SSO_TEAM = "canonical-content-people"
LAUNCHPAD_API_URL = "https://api.launchpad.net/1.0"


def _safe_redirect_url(target):
    if target and urlparse(target).netloc == "":
        return target
    return "/manager"


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
            return flask.redirect(
                _safe_redirect_url(flask.request.args.get("next"))
            )

        redirect_uri = flask.url_for("oauth_callback", _external=True)
        return oauth.canonical.authorize_redirect(redirect_uri)

    @app.route("/auth/callback")
    def oauth_callback():
        token = oauth.canonical.authorize_access_token()
        users, status_code = get_users_data(token["userinfo"]["name"])

        if status_code != 200 or not users:
            flask.abort(
                403, description="Failed to fetch user data from directory."
            )

        response = requests.get(
            f"{LAUNCHPAD_API_URL}/~{users[0]['launchpadId']}/super_teams",
        )

        if response.status_code != 200:
            flask.abort(
                403, description="Failed to fetch Launchpad team memberships."
            )

        memberships = response.json().get("entries", [])
        if SSO_TEAM not in [team["name"] for team in memberships]:
            flask.abort(
                403,
                description=(
                    "Please make sure you are a member of the "
                    "canonical-content-people team on Launchpad."
                ),
            )

        flask.session["openid"] = {
            "identity_url": token["userinfo"]["iss"],
            "email": token["userinfo"]["email"],
            "fullname": token["userinfo"]["name"],
        }

        return flask.redirect(
            _safe_redirect_url(flask.request.args.get("next"))
        )


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
