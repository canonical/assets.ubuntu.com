# System
from copy import copy

# Modules
from mongomock import Connection

# Local
from assets_server.mappers import RedirectManager


class TestRedirectManager:
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

    def get_manager(self):
        """
        A provisioned mock collection for testing
        """

        self.collection = Connection().db.collection
        self.collection.insert(copy(self.redirect_one))
        self.collection.insert(copy(self.redirect_two))
        self.collection.insert(copy(self.redirect_three))

        return RedirectManager(self.collection)

    def test_exists(self):
        manager = self.get_manager()

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

        assert response_one is True
        assert response_two is True
        assert response_three is True
        assert response_four is False

    def test_fetch(self):
        manager = self.get_manager()

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
        assert response_one == expected_one
        assert response_two == self.redirect_two
        assert response_three == self.redirect_three
        assert response_four is None

    def test_create(self):
        manager = self.get_manager()

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

        assert response_new == new_redirect
        assert new_record['redirect_path'] == new_redirect['redirect_path']
        assert new_record['target_url'] == new_record['target_url']

    def test_update(self):
        manager = self.get_manager()

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

        assert update_response['redirect_path'] == new_redirect_path
        assert found_record['redirect_path'] == new_redirect_path
        assert update_response['target_url'] == new_target_url
        assert found_record['target_url'] == new_target_url
        assert update_response['permanent'] is True
        assert found_record['permanent'] is True

    def test_all(self):
        manager = self.get_manager()

        all_redirects = manager.all()

        expected_one = self.redirect_one
        expected_one['permanent'] = False
        assert sorted(all_redirects) == sorted([
            expected_one,
            self.redirect_two,
            self.redirect_three
        ])

    def test_delete(self):
        manager = self.get_manager()

        delete_path = self.redirect_one['redirect_path']

        assert manager.exists(delete_path)

        manager.delete(delete_path)

        assert not manager.exists(delete_path)
        assert not self.collection.find_one(self.redirect_one)
