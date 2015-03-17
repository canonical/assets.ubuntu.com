from api_test_helpers import get, token_fixture, post, delete


class TestAssetsAPI:
    """
    API tests of the assets server.
    """

    params = {
        'token': token_fixture()
    }

    def test_no_token(self):
        """
        Tests that no token gives a Forbidden.
        """
        assert get().status_code == 403

    def test_bad_token(self):
        """
        Tests a bad token gives a Forbidden.
        """
        assert get(params={'token': 'bad'}).status_code == 403, (
            "Using a bad token was not forbidden as expected.")

    def test_token(self):
        """
        Tests a good token returns a 200 at the root.
        """
        assert get(params=self.params).status_code == 200, (
            "Token '{0}' failed to authenticate correctly".format(self.token)
        )

    def test_upload_and_delete_file(self):
        """
        Tests uploading an asset, getting that asset and deleting it.
        """
        post_response = post(
            params=self.params,
            data={
                'asset': "Test",
                'friendly-name': "test_friendly_name",
                'tags': "tags",
                'type': 'base64'
            }
        )
        assert post_response.status_code == 201, (
            "Asset not created correctly."
        )

        file_path = post_response.json()['file_path']

        assert get(path=file_path, params=self.params).status_code == 200, (
            "Asset not downloaded correctly"
        )

        assert delete(path=file_path, params=self.params).status_code == 200, (
            "Asset not deleted successfully."
        )
