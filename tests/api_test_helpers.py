import requests
import os
import sys
from functools import wraps

from requests import ConnectionError

default_server_url = "http://localhost:8012/v1/"


def token_fixture(fixtures_path=None):
    """
    Get the token from the fixture file
    """

    token = ''

    if not fixtures_path:
        this_dir = os.path.dirname(os.path.realpath(__file__))
        fixtures_path = '{0}/fixtures'.format(this_dir)

    token_path = '{fixtures}/api-token'.format(fixtures=fixtures_path)

    if os.path.isfile(token_path):
        with open(token_path) as token_file:
            token = token_file.read().rstrip()

    if not token:
        sys.exit('Please add a valid token in {0}'.format(token_path))

    return token


def exit_if_server_not_found(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ConnectionError as e:
            sys.exit(
                'No server found: {0}'.format(e)
            )
    return wrapper


@exit_if_server_not_found
def get(path="", params={}, server_url=default_server_url):
    """
    Convienince function for making simple GETs
    """
    exit_if_server_not_found(server_url)

    return requests.get(server_url + path, params=params)


@exit_if_server_not_found
def post(data={}, path="", params={}, server_url=default_server_url):
    """
    Convienince function for making simple POSTs
    """
    exit_if_server_not_found(server_url)

    return requests.post(server_url + path, params=params, data=data)


@exit_if_server_not_found
def delete(path="", params={}, server_url=default_server_url):
    """
    Convienince function for making simple DELETEs
    """
    exit_if_server_not_found(server_url)

    return requests.delete(server_url + path, params=params)
