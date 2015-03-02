import errno
import re
import mimetypes
import urllib
import uuid
from hashlib import sha1

from wand.image import Image
from swiftclient.exceptions import ClientException as SwiftException

from lib.file_helpers import file_error


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
    mimes = {
        "png": "image/png",
        "svg": "image/svg+xml"
    }

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
                urllib.quote(file_path),
                file_data
            )
        except SwiftException as swift_error:
            if swift_error.http_status == 404:
                # Not found, assuming container doesn't exist
                self.swift_connection.put_container(self.container_name)

                # And try to create again
                self.swift_connection.put_object(
                    self.container_name,
                    urllib.quote(file_path),
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
                urllib.quote(file_path)
            )
        except SwiftException as error:
            if error.http_status == 404:
                file_exists = False

        return file_exists

    def fetch(self, file_path):
        sub_path = file_path[:-4]
        mimetype = mimetypes.guess_type(file_path)[0]
        sub_mimetype = mimetypes.guess_type(sub_path)[0]
        svg_to_png = False
        asset_data = None

        if (
            mimetype == self.mimes["png"] and
            sub_mimetype == self.mimes["svg"] and
            not self.exists(file_path)
        ):
            # Remove extra ".png" extension
            file_path = sub_path
            svg_to_png = True

        encoded_path = urllib.quote(file_path)

        asset = self.swift_connection.get_object(
            self.container_name,
            encoded_path
        )
        asset_data = asset[1]

        # Convert to png (if applicable)
        if svg_to_png:
            with Image(blob=asset_data, format="svg") as image:
                asset_data = image.make_blob("png")

        return asset_data

    def headers(self, file_path):
        return self.swift_connection.head_object(
            self.container_name,
            file_path
        )

    def delete(self, file_path):
        self.swift_connection.delete_object(
            self.container_name,
            urllib.quote(file_path)
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
        search = {"file_path": file_path}

        data = {
            "file_path": file_path,
            "tags": tags
        }

        self.data_collection.update(search, data, True)

        return self.fetch_one(file_path)

    def fetch_one(self, file_path):
        asset_data = self.data_collection.find_one(
            {"file_path": file_path}
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

        mimetype = mimetypes.guess_type(asset_data['file_path'])[0]

        if mimetype == "image/svg+xml":
            asset_data['png_file_path'] = asset_data['file_path'] + ".png"

        return asset_data

    def fetch(self, file_paths):
        return [
            self.fetch_one(file_path)
            for file_path in file_paths
        ]

    def delete(self, file_path):
        self.data_collection.remove({'file_path': file_path})


class TokenManager:

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
