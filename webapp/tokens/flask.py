import flask

import webapp.tokens.mapper as token_mapper
from webapp.decorators import token_required


tokens_blueprint = flask.Blueprint("tokens", __name__)


@tokens_blueprint.route("/tokens", methods=["GET"])
@token_required
def get_tokens():
    tokens = token_mapper.get_all_tokens()
    return (
        flask.jsonify(
            [{"name": token.name, "token": token.token} for token in tokens]
        ),
        200,
    )


@tokens_blueprint.route("/tokens/<string:name>", methods=["GET"])
@token_required
def get_token(name):
    token = token_mapper.find_token_by_name(name)

    if not token:
        flask.abort(404)

    return flask.jsonify({"name": token.name, "token": token.token})


@tokens_blueprint.route("/tokens/<string:name>", methods=["POST"])
@token_required
def create_token(name):
    if not name:
        flask.abort(400, "Missing required field 'name'")

    if token_mapper.find_token_by_name(name):
        flask.abort(400, "A token with this name already exists")

    token = token_mapper.create_token(name)

    return flask.jsonify({"name": token.name, "token": token.token}), 201


@tokens_blueprint.route("/tokens/<string:name>", methods=["DELETE"])
@token_required
def delete_token(name):
    deleted = token_mapper.delete_token_by_name(name)

    if not deleted:
        flask.abort(404, f"No token named '{name}'")

    return flask.jsonify({}), 204
