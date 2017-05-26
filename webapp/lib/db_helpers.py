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
