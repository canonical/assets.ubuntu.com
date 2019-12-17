# Standard library
import uuid

# Packages
import click
import flask

# Local
from webapp.database import db_session
from webapp.models import Token


token_group = flask.cli.AppGroup("token")


@token_group.command("create")
@click.argument("name")
def create_token(name):
    if db_session.query(Token).filter(Token.name == name).one_or_none():
        print(f"Token exists: {name}")
    else:
        token = Token(name=name, token=uuid.uuid4().hex)
        db_session.add(token)
        db_session.commit()
        print(f"Token created: {token.name} - {token.token}")


@token_group.command("delete")
@click.argument("name")
def delete_token(name):
    token = db_session.query(Token).filter(Token.name == name).one_or_none()

    if not token:
        print(f"Token not found: '{name}'")
    else:
        db_session.delete(token)
        db_session.commit()
        print(f"Token deleted: '{name}'")


@token_group.command("list")
def list_token():
    tokens = db_session.query(Token).all()

    if tokens:
        for token in tokens:
            print(f"{token.name} - {token.token}")
    else:
        print("No tokens found")
