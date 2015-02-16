import requests

BASE_URL = "http://localhost:8012/v1/"


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
        assert get({'token': 'badtoken'}).status_code == 403
