import re
import uuid
from hashlib import sha1

from swiftclient.exceptions import ClientException as SwiftException

from lib.url_helpers import normalize


class FileManager:
    """
    Manage asset files:
    - creation
    - retrieval
    - searching
    - deletion
    """

    container_name = "assets"
    swift_connection = None

    def __init__(self, swift_connection):
        self.swift_connection = swift_connection

    def create(self, file_data, file_path):
        """
        Create a new asset and return its file_path
        If it already exists,
        return the file_path for the existing asset
        (don't create it again)
        """

        try:
            # Create object
            self.swift_connection.put_object(
                self.container_name,
                normalize(file_path),
                file_data
            )
        except SwiftException as swift_error:
            if swift_error.http_status == 404:
                # Not found, assuming container doesn't exist
                self.swift_connection.put_container(self.container_name)

                # And try to create again
                self.swift_connection.put_object(
                    self.container_name,
                    normalize(file_path),
                    file_data
                )
            else:
                # Otherwise, throw the exception again
                raise swift_error

    def exists(self, file_path):
        file_exists = True

        try:
            self.swift_connection.head_object(
                self.container_name,
                normalize(file_path)
            )
        except SwiftException as error:
            if error.http_status == 404:
                file_exists = False

        return file_exists

    def fetch(self, file_path):
        asset_data = None

        asset = self.swift_connection.get_object(
            self.container_name,
            normalize(file_path)
        )
        asset_data = asset[1]

        return asset_data

    def headers(self, file_path):
        return self.swift_connection.head_object(
            self.container_name,
            normalize(file_path)
        )

    def delete(self, file_path):
        if self.exists(file_path):
            self.swift_connection.delete_object(
                self.container_name,
                normalize(file_path)
            )
            return True

    def generate_asset_path(self, file_data, friendly_name):
        """
        Generate a unique asset file_path
        based on a friendly name
        """

        path = sha1(file_data).hexdigest()[:8]
        if friendly_name:
            path += '-' + friendly_name

        return path


class DataManager:
    """
    Generate data objects for assets
    """

    request = None
    data_collection = None

    def __init__(self, data_collection):
        self.data_collection = data_collection

    def update(self, file_path, tags):
        search = {"file_path": normalize(file_path)}

        data = {
            "file_path": normalize(file_path),
            "tags": tags
        }

        self.data_collection.update(search, data, True)

        return self.fetch_one(file_path)

    def fetch_one(self, file_path):
        asset_data = self.data_collection.find_one(
            {"file_path": normalize(file_path)}
        )

        return self.format(asset_data) if asset_data else None

    def find(self, query):
        match = re.compile(query)

        results = self.data_collection.find(
            {
                '$or': [
                    {'file_path': match},
                    {'tags': match}
                ]
            }
        )

        return [
            self.format(asset_data)
            for asset_data in results
        ]

    def exists(self, file_path):
        return bool(self.fetch_one(file_path))

    def format(self, asset_record):
        asset_data = {
            'file_path': asset_record['file_path'],
            'tags': asset_record["tags"] or "",
            'created': asset_record["_id"].generation_time.ctime()
        }

        return asset_data

    def fetch(self, file_paths):
        return [
            self.fetch_one(file_path)
            for file_path in file_paths
        ]

    def delete(self, file_path):
        if self.exists(file_path):
            return self.data_collection.remove({'file_path': file_path})


class TokenManager:
    """
    A class for maintaining authentication tokens
    in a MongoDB database
    """

    def __init__(self, data_collection):
        self.data_collection = data_collection

    def exists(self, name):
        """Check if a token already exists with a specified name"""

        return bool(self.fetch(name))

    def authenticate(self, token):
        """Check if this authentication token is valid (i.e. exists)"""

        return bool(
            self.data_collection.find_one(
                {'token': token}
            )
        )

    def fetch(self, name):
        """Get a token's data, by its name"""

        token_record = self.data_collection.find_one(
            {"name": name}
        )
        return self._format(token_record)

    def create(self, name):
        """Generate a random token, with a given name"""

        data = {
            'token': uuid.uuid4().get_hex(),  # Random UUID
            'name': name
        }

        if not self.exists(name):
            if self.data_collection.insert(data):
                return data

    def delete(self, name):
        """Delete tokens with this name"""
        token = self.fetch(name)

        if token:
            self.data_collection.remove({'name': name})
            return token

    def all(self):
        """Get a list of all tokens"""

        return [self._format(record) for record in self.data_collection.find()]

    def _format(self, token_record):
        if token_record:
            return {
                'token': token_record['token'],
                'name': token_record['name']
            }


class RedirectManager:
    """
    Manage 301 redirects stored in a MongoDB database
    """

    def __init__(self, data_collection):
        self.data_collection = data_collection

    def exists(self, redirect_path):
        """
        Check if a redirect URL already exists with a specified name
        """

        return bool(self.fetch(redirect_path))

    def fetch(self, redirect_path):
        """
        Get a redirect's data, by its URL path
        """

        redirect_record = self.data_collection.find_one(
            {"redirect_path": redirect_path}
        )
        return self._format(redirect_record)

    def update(self, redirect_path, target_url):
        """
        Create or update redirect, by setting a target URL
        for a local URL path
        """

        search = {"redirect_path": redirect_path}

        data = {
            "redirect_path": redirect_path,
            "target_url": target_url
        }

        self.data_collection.update(search, data, True)

        return self.fetch(redirect_path)

    def delete(self, redirect_path):
        """
        Delete redirect with this URL path
        """

        redirect_record = self.fetch(redirect_path)

        if redirect_record:
            self.data_collection.remove({'redirect_path': redirect_path})
            return redirect_record

    def all(self):
        """
        Get a list of all redirect
        """

        return [self._format(record) for record in self.data_collection.find()]

    def _format(self, redirect_record):
        if redirect_record:
            return {
                'redirect_path': redirect_record['redirect_path'],
                'target_url': redirect_record['target_url']
            }
