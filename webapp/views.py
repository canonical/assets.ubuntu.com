# Standard library
import uuid

# Packages
import flask

# Local
from webapp.decorators import token_required
from webapp.database import db_session
from webapp.models import Token


@token_required
def index():
    return {}, 200


# Tokens
# ===

@token_required
def get_tokens():
    tokens = db_session.query(Token).all()
    return (
        flask.jsonify(
            [{"name": token.name, "token": token.token} for token in tokens]
        ),
        200,
    )


@token_required
def get_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        flask.abort(404)

    return flask.jsonify({"name": token.name, "token": token.token})


@token_required
def create_token(name):
    if not name:
        flask.abort(400, "Missing required field 'name'")

    if db_session.query(Token).filter(Token.name == name).one_or_none():
        flask.abort(400, "A token with this name already exists")

    token = Token(name=name, token=uuid.uuid4().hex)
    db_session.add(token)
    db_session.commit()

    return flask.jsonify({"name": token.name, "token": token.token}), 201


@token_required
def delete_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        flask.abort(404, f"No token named '{name}'")

    db_session.delete(token)
    db_session.commit()

    return flask.jsonify({}), 204
