from api_test_helpers import get, get_token

class TestAssetsAPI:
    """
    API tests of the assets server.
    """

    token = get_token()

    def test_no_token(self):
        assert get().status_code == 403

    def test_bad_token(self):
        params = {'token': 'badtoken'}
        assert get(params).status_code == 403

    def test_token(self):
        params = {'token': self.token}
        assert get(params).status_code == 200, (
            "Token '{0}' failed to authenticate correctly".format(self.token)
        )
