import requests
import os
import sys


def get(params={}, server_url="http://localhost:8012/v1/"):
    """
    Convienince function for making simple GETs
    """

    try:
        requests.get(server_url)
    except:
        sys.exit(
            'No server found on {0}'.format(server_url)
        )

    return requests.get(server_url, params=params)


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
