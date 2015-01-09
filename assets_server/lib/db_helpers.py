# Base packages
import os
from uuid import uuid4

# Modules
from pymongo import MongoClient
from pymongo.errors import ConfigurationError


def mongo_db_from_url(mongo_url, default_database):
    """
    Get the mongodb connection from a mongo URL
    if the URL doesn't provide a database, use the
    `default_database`.
    Defaulting mongo URL is mongodb://localhost/assets
    """

    if not mongo_url:
        mongo_url = 'mongodb://localhost/'

    mongo = MongoClient(mongo_url)

    try:
        database = mongo.get_default_database()
    except ConfigurationError:
        database = mongo[default_database]

    return database


def auth_token(token_name='server'):
    """
    Retrieve server auth token from DB,
    or create it if it doesn't exist
    """

    database = mongo_db_from_url(
        mongo_url=os.environ.get('MONGO_URL'),
        default_database='assets'
    )
    tokens = database.tokens

    if not tokens.find_one({'name': token_name}):
        tokens.insert({'name': token_name, 'token': uuid4().get_hex()})

    return tokens.find_one({'name': token_name})['token']
