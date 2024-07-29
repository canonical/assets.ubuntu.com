import unittest
import unittest.mock

from webapp.app import app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """
        Set up Flask app for testing
        """
        app.testing = True
        self.client = app.test_client()

    def test_homepage_no_token(self):
        """
        When given the index URL without token,
        we should return a 401 status code
        """

        response = self.client.get("/v1")
        self.assertEqual(response.status_code, 401)

    def test_not_found(self):
        """
        When given a non-existent URL,
        we should return a 404 status code
        """
        response = self.client.get("/image.png", follow_redirects=True)
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_existing_asset(self):
        """
        When given an existing asset URL,
        we should return a 200 status code
        """
        with unittest.mock.patch(
            "webapp.swift.file_manager.fetch"
        ) as mock_fetch, unittest.mock.patch(
            "webapp.swift.file_manager.headers"
        ) as mock_headers:
            mock_fetch.return_value = b"image data"
            mock_headers.return_value = {
                "last-modified": "Mon, 29 Jul 2024 17:29:55 GMT"
            }

            response = self.client.get("/image.png", follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            mock_fetch.assert_called_once_with("image.png")
            mock_headers.assert_called_once_with("image.png")


if __name__ == "__main__":
    unittest.main()
