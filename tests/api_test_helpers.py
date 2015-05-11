import requests
import os
import sys
from errno import ECONNREFUSED

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


def exit_if_server_not_found():
    try:
        requests.get(default_server_url)
    except ConnectionError as e:
        errno = e.args[0].reason.errno
        lookup_error = {
            ECONNREFUSED: "No server found: ",
            -2: "Unknown error: "
        }
        sys.exit(
            '{0}{1}'.format(lookup_error.get(errno), e)
        )


def get(path="", params={}, server_url=default_server_url):
    """
    Convienince function for making simple GETs
    """

    return requests.get(server_url + path, params=params)


def post(data={}, path="", params={}, server_url=default_server_url):
    """
    Convienince function for making simple POSTs
    """

    return requests.post(server_url + path, params=params, data=data)


def delete(path="", params={}, server_url=default_server_url):
    """
    Convienince function for making simple DELETEs
    """

    return requests.delete(server_url + path, params=params)
