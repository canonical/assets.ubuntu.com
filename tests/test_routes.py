import unittest
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

        self.assertEqual(self.client.get("/v1").status_code, 401)

    def test_not_found(self):
        """
        When given a non-existent URL,
        we should return a 404 status code
        """

        self.assertEqual(self.client.get("/not-found-url").status_code, 404)


if __name__ == "__main__":
    unittest.main()
