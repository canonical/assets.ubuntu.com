# Standard library
from datetime import datetime
import re
import uuid

# Packages
import click
import flask
import requests

# Local
from webapp.database import db_session
from webapp.models import Asset, Redirect, Token
from webapp.services import asset_service

token_group = flask.cli.AppGroup("token")
db_group = flask.cli.AppGroup("database")


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


@db_group.command("import-assets-from-prod")
@click.argument("token")
def import_assets_from_prod(token):
    print("Assets in DB count (before):", db_session.query(Asset).count())
    data = requests.get(f"https://assets.ubuntu.com/v1?token={token}").json()
    print("Data to insert:", len(data))
    for index in range(len(data)):
        if index % 1000 == 0:
            print(f"{index}/{len(data)}")
        entry = data[index]
        file_path = entry.get("file_path")
        created = datetime.strptime(
            entry.get("created"), "%a %b %d %H:%M:%S %Y"
        )
        tags = entry.get("tags", "")
        tags = re.split(",|\\s", tags)
        entry.pop("file_path", None)
        entry.pop("created", None)
        entry.pop("tags", None)

        # rename optimized
        if entry.get("optimized", None):
            entry["optimize"] = entry.get("optimized", None)

        asset = asset_service.find_asset(file_path)
        # update all the fields if already exists
        if asset:
            asset_service.update_asset(file_path, tags)
        else:
            asset = Asset(file_path=file_path, data=entry, created=created)
            db_session.add(asset)
            asset.tags = asset_service.create_tags_if_not_exist(tags)
            db_session.commit()
    print("Assets in DB count (after):", db_session.query(Asset).count())


@db_group.command("import-redirects-from-prod")
@click.argument("token")
def import_redirects_from_prod(token):
    data = requests.get(
        f"https://assets.ubuntu.com/v1/redirects?token={token}"
    ).json()

    print("Importing redirects...")
    for entry in data:
        db_session.add(
            Redirect(
                permanent=entry.get("permanent"),
                redirect_path=entry.get("redirect_path"),
                target_url=entry.get("target_url"),
            )
        )

    db_session.commit()
    print("Done!")


@db_group.command("insert-dummy-data")
def insert_dummy_data():
    dummy_pdf = {
        "name": "dummy.pdf",
        "file": open("./webapp/dummy-data/dummy.pdf", "rb").read(),
    }
    ubuntu_png = {
        "name": "ubuntu.png",
        "file": open("./webapp/dummy-data/ubuntu.png", "rb").read(),
        "optimize": True,
    }
    ubuntu_svg = {
        "name": "ubuntu.svg",
        "file": open("./webapp/dummy-data/ubuntu.svg", "rb").read(),
    }

    assets_to_create = [dummy_pdf, ubuntu_png, ubuntu_svg]
    for asset in assets_to_create:
        asset_service.create_asset(
            file_content=asset["file"],
            friendly_name=asset["name"],
            optimize=asset.get("optimize", False),
            tags=["dummy_asset"],
        )
