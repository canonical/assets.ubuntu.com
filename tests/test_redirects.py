# System
import os
import sys
from copy import copy

# Modules
from mongomock import Connection

# Local
file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(file_path)
parent_directory = os.path.dirname(current_directory)
app_directory = os.path.join(parent_directory, 'assets_server')
sys.path.insert(1, app_directory)
from mappers import RedirectManager


class TestRedirectManager:
    """
    Test the RedirectRecord model.
    """

    redirect_one = {
        'redirect_path': 'hello/world.fish/and.chips',
        'target_url': 'https://example.com/something'
    }
    redirect_two = {
        'redirect_path': 'what-now',
        'target_url': '/something-else'
    }

    collection = None

    def get_manager(self):
        """
        A provisioned mock collection for testing
        """

        self.collection = Connection().db.collection
        self.collection.insert(copy(self.redirect_one))
        self.collection.insert(copy(self.redirect_two))

        return RedirectManager(self.collection)

    def test_exists(self):
        manager = self.get_manager()

        response_one = manager.exists(
            redirect_path=self.redirect_one['redirect_path']
        )
        response_two = manager.exists(
            redirect_path=self.redirect_two['redirect_path']
        )
        response_three = manager.exists('non-existent')

        assert response_one is True
        assert response_two is True
        assert response_three is False

    def test_fetch(self):
        manager = self.get_manager()

        response_one = manager.fetch(
            self.redirect_one['redirect_path']
        )
        response_two = manager.fetch(
            self.redirect_two['redirect_path']
        )
        response_three = manager.fetch('some/other/path')

        assert response_one == self.redirect_one
        assert response_two == self.redirect_two
        assert response_three is None

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

        assert response_new == new_redirect
        assert new_record['redirect_path'] == new_redirect['redirect_path']
        assert new_record['target_url'] == new_record['target_url']

    def test_update(self):
        manager = self.get_manager()

        update_redirect = {
            'redirect_path': self.redirect_one['redirect_path'],
            'target_url': 'http://example.com/another_path'
        }

        response_updated = manager.update(
            redirect_path=update_redirect['redirect_path'],
            target_url=update_redirect['target_url']
        )

        updated_record = self.collection.find_one(update_redirect)

        assert response_updated == response_updated
        updated_redirect_path = update_redirect['redirect_path']
        updated_target_url = update_redirect['target_url']
        assert updated_record['redirect_path'] == updated_redirect_path
        assert updated_record['target_url'] == updated_target_url

    def test_all(self):
        manager = self.get_manager()

        all_redirects = manager.all()

        assert sorted(all_redirects) == sorted([
            self.redirect_one,
            self.redirect_two
        ])

    def test_delete(self):
        manager = self.get_manager()

        delete_path = self.redirect_one['redirect_path']

        assert manager.exists(delete_path)

        manager.delete(delete_path)

        assert not manager.exists(delete_path)
        assert not self.collection.find_one(self.redirect_one)
