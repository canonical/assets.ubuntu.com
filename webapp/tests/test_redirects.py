# Core packages
from copy import copy

# Third-party packages
from mongomock import MongoClient
from django.test import SimpleTestCase

# Local packages
from webapp.mappers import RedirectManager


class TestRedirectManager(SimpleTestCase):
    """
    Test the RedirectRecord model.
    """

    redirect_one = {
        'redirect_path': 'hello/world.fish/and.chips',
        'target_url': 'https://example.com/something'
    }
    redirect_two = {
        'permanent': False,
        'redirect_path': 'what-now',
        'target_url': '/something-else'
    }
    redirect_three = {
        'permanent': True,
        'redirect_path': 'third-redirect',
        'target_url': '/third-target'
    }

    collection = None

    def _get_manager(self):
        """
        A provisioned mock collection for testing
        """

        self.collection = MongoClient().db.collection
        self.collection.insert(copy(self.redirect_one))
        self.collection.insert(copy(self.redirect_two))
        self.collection.insert(copy(self.redirect_three))

        return RedirectManager(self.collection)

    def test_exists(self):
        manager = self._get_manager()

        response_one = manager.exists(
            redirect_path=self.redirect_one['redirect_path']
        )
        response_two = manager.exists(
            redirect_path=self.redirect_two['redirect_path']
        )
        response_three = manager.exists(
            redirect_path=self.redirect_three['redirect_path']
        )
        response_four = manager.exists('non-existent')

        self.assertTrue(response_one)
        self.assertTrue(response_two)
        self.assertTrue(response_three)
        self.assertFalse(response_four)

    def test_fetch(self):
        manager = self._get_manager()

        response_one = manager.fetch(
            self.redirect_one['redirect_path']
        )
        response_two = manager.fetch(
            self.redirect_two['redirect_path']
        )
        response_three = manager.fetch(
            self.redirect_three['redirect_path']
        )
        response_four = manager.fetch('some/other/path')

        expected_one = self.redirect_one
        expected_one['permanent'] = False

        self.assertEqual(response_one, expected_one)
        self.assertEqual(response_two, self.redirect_two)
        self.assertEqual(response_three, self.redirect_three)
        self.assertIsNone(response_four)

    def test_create(self):
        manager = self._get_manager()

        new_redirect = {
            'redirect_path': 'new/redirect',
            'target_url': 'http://example.com/some_path'
        }
        response_new = manager.update(
            redirect_path=new_redirect['redirect_path'],
            target_url=new_redirect['target_url']
        )
        new_record = self.collection.find_one(new_redirect)
        new_redirect['permanent'] = False

        self.assertEqual(response_new, new_redirect)
        self.assertEqual(
            new_record['redirect_path'], new_redirect['redirect_path']
        )
        self.assertEqual(new_record['target_url'], new_record['target_url'])

    def test_update(self):
        manager = self._get_manager()

        new_redirect = {
            'redirect_path': self.redirect_three['redirect_path'],
            'target_url': 'http://example.com/another_path'
        }

        update_response = manager.update(
            redirect_path=new_redirect['redirect_path'],
            target_url=new_redirect['target_url']
        )

        found_record = self.collection.find_one({
            "redirect_path": new_redirect['redirect_path']
        })

        new_redirect_path = new_redirect['redirect_path']
        new_target_url = new_redirect['target_url']

        self.assertEqual(update_response['redirect_path'], new_redirect_path)
        self.assertEqual(found_record['redirect_path'], new_redirect_path)
        self.assertEqual(update_response['target_url'], new_target_url)
        self.assertEqual(found_record['target_url'], new_target_url)
        self.assertTrue(update_response['permanent'])
        self.assertTrue(found_record['permanent'])

    def test_all(self):
        manager = self._get_manager()

        all_redirects = manager.all()

        expected_one = self.redirect_one
        expected_one['permanent'] = False
        self.assertEqual(
            sorted(all_redirects, key=lambda x: x['redirect_path']),
            sorted(
                [expected_one, self.redirect_two, self.redirect_three],
                key=lambda x: x['redirect_path']
            )
        )

    def test_delete(self):
        manager = self._get_manager()

        delete_path = self.redirect_one['redirect_path']

        assert manager.exists(delete_path)

        manager.delete(delete_path)

        self.assertFalse(manager.exists(delete_path))
        self.assertFalse(self.collection.find_one(self.redirect_one))
