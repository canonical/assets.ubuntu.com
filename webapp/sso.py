import functools

import flask
from django_openid_auth.teams import TeamsRequest, TeamsResponse
from flask_openid import OpenID


SSO_LOGIN_URL = "https://login.ubuntu.com"
SSO_TEAM = "canonical-content-people"


def init_sso(app):
    open_id = OpenID(
        stateless=True, safe_roots=[], extension_responses=[TeamsResponse]
    )

    @app.route("/login", methods=["GET", "POST"])
    @open_id.loginhandler
    def login():
        if "openid" in flask.session:
            return flask.redirect(open_id.get_next_url())

        teams_request = TeamsRequest(query_membership=[SSO_TEAM])
        return open_id.try_login(
            SSO_LOGIN_URL, ask_for=["email"], extensions=[teams_request]
        )

    @open_id.after_login
    def after_login(resp):
        if SSO_TEAM not in resp.extensions["lp"].is_member:
            flask.abort(403)

        flask.session["openid"] = {
            "identity_url": resp.identity_url,
            "email": resp.email,
        }

        return flask.redirect(open_id.get_next_url())


def login_required(func):
    """
    Decorator that checks if a user is logged in, and redirects
    to login page if not.
    """

    @functools.wraps(func)
    def is_user_logged_in(*args, **kwargs):
        if "openid" not in flask.session:
            return flask.redirect("/login?next=" + flask.request.path)

        return func(*args, **kwargs)

    return is_user_logged_in
