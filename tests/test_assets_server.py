import sys

import requests
from test_token import token

BASE_URL = "http://localhost:8012/v1/"


if token == "dummy":
    sys.exit('Please add a valid token in test_token.py')

try:
    requests.get(BASE_URL)
except:
    sys.exit(
        'No server found on {url}'.format(
            url=BASE_URL
        )
    )


def get(params={}):
    """
    Convienince function for making simple GETs
    """

    return requests.get(BASE_URL, params=params)


class TestAssetsAPI:
    """
    API tests of the assets server.
    """

    def test_no_token(self):
        assert get().status_code == 403

    def test_bad_token(self):
        params = {'token': 'badtoken'}
        assert get(params).status_code == 403

    def test_token(self):
        params = {'token': token}
        assert get(params).status_code == 200
