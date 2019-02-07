# Core packages
import argparse
import uuid
import sys
import errno

# Third-party packages
import requests


parser = argparse.ArgumentParser()
parser.add_argument(
    "server_url",
    help="URL for the server to test, e.g. http://localhost:8017/v1/",
)
parser.add_argument("token", help="An authentication token for the server.")
args = parser.parse_args()
server_url = args.server_url
token = args.token


def exit_if_server_not_found():
    try:
        requests.get(server_url)
    except ConnectionError as e:
        error_number = e.args[0].reason.errno
        lookup_error = {
            errno.ECONNREFUSED: "No server found: ",
            -2: "Unknown error: ",
        }
        sys.exit("{0}{1}".format(lookup_error.get(error_number), e))


def get(path="", params={}, server_url=server_url):
    """
    Convienince function for making simple GETs
    """

    return requests.get(server_url + path, params=params)


def post(data={}, path="", params={}, server_url=server_url):
    """
    Convienince function for making simple POSTs
    """

    return requests.post(server_url + path, params=params, data=data)


def delete(path="", params={}, server_url=server_url):
    """
    Convienince function for making simple DELETEs
    """

    return requests.delete(server_url + path, params=params)


class TestAssetsAPI:
    """
    API tests of the assets server.
    """

    def test_no_token(self):
        """
        Tests that no token gives a Forbidden.
        """
        assert get().status_code == 403

    def test_bad_token(self):
        """
        Tests a bad token gives a Forbidden.
        """
        assert (
            get(params={"token": "bad"}).status_code == 403
        ), "Using a bad token was not forbidden as expected."

    def test_token(self):
        """
        Tests a good token returns a 200 at the root.
        """
        assert (
            get(params={"token": token}).status_code == 200
        ), "Token '{0}' failed to authenticate correctly".format(token)

    def test_upload_and_delete_file(self):
        """
        Tests uploading an asset, getting that asset and deleting it.
        """

        post_response = post(
            params={"token": token},
            data={
                "asset": uuid.uuid4().hex,
                "friendly-name": "test_friendly_name",
                "tags": "tags",
                "type": "base64",
            },
        )

        assert post_response.status_code == 201, "Asset not created correctly."

        file_path = post_response.json()["file_path"]

        assert (
            get(path=file_path, params={"token": token}).status_code == 200
        ), "Asset not downloaded correctly"

        assert (
            delete(path=file_path, params={"token": token}).status_code == 200
        ), "Asset not deleted successfully."


if __name__ == "__main__":
    tests = TestAssetsAPI()
    tests.test_no_token()
    tests.test_bad_token()
    tests.test_token()
    tests.test_upload_and_delete_file()
    print("All tests passed")
