import requests

BASE_URL = "https://assets.staging.ubuntu.com/v1/"


def get(params={}):
    return requests.get(BASE_URL, params=params)


class TestAssetsAPI:

    def test_no_token(self):
        assert get().status_code == 403

    def test_unauthorised(self):
        assert get({'token': 'badtoken'}).status_code == 403
