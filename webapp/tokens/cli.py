import click
import flask

import webapp.tokens.mapper as token_mapper


token_cli = flask.cli.AppGroup("token")


@token_cli.command("create")
@click.argument("name")
def create_token(name):
    if token_mapper.find_token_by_name(name):
        print(f"Token exists: {name}")
    else:
        token = token_mapper.create_token(name)
        print(f"Token created: {token.name} - {token.token}")


@token_cli.command("delete")
@click.argument("name")
def delete_token(name):
    deleted = token_mapper.delete_token_by_name(name)

    if not deleted:
        print(f"Token not found: '{name}'")
    else:
        print(f"Token deleted: '{name}'")


@token_cli.command("list")
def list_token():
    tokens = token_mapper.get_all_tokens()

    if tokens:
        for token in tokens:
            print(f"{token.name} - {token.token}")
    else:
        print("No tokens found")
