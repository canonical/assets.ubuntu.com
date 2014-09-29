import re
import mimetypes
import urllib
import uuid
from hashlib import sha1

from wand.image import Image
from swiftclient.client import ClientException as SwiftException


class DelayedConnection:
    """
    Get read to make a Connection, for the FileManager
    but only actually make the connection when "manager" if first called
    """

    file_manager = False

    def __init__(
        self, manager_class, connection_class,
        auth_url, username, password, auth_version, tenant_name
    ):
        self.manager_class = manager_class
        self.connection_class = connection_class
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.auth_version = auth_version
        self.tenant_name = tenant_name

    def manager(self):
        if not self.file_manager:
            self.file_manager = self.manager_class(
                self.connection_class(
                    self.auth_url,
                    self.username,
                    self.password,
                    auth_version=self.auth_version,
                    os_options={'tenant_name': self.tenant_name}
                )
            )

        return self.file_manager


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

        # Make sure container exists
        self.swift_connection.put_container(self.container_name)

    def create(self, file_data, filename):
        """
        Create a new asset and return its filename
        If it already exists,
        return the filename for the existing asset
        (don't create it again)
        """

        # Create object
        self.swift_connection.put_object(
            self.container_name,
            urllib.quote(filename),
            file_data
        )

    def exists(self, filename):
        file_exists = True

        try:
            self.swift_connection.head_object(
                self.container_name,
                urllib.quote(filename)
            )
        except SwiftException as error:
            if error.http_status == 404:
                file_exists = False

        return file_exists

    def fetch(self, filename):
        sub_filename = filename[:-4]
        mimetype = mimetypes.guess_type(filename)[0]
        sub_mimetype = mimetypes.guess_type(sub_filename)[0]
        svg_to_png = False
        asset_data = None

        if (
            mimetype == self.mimes["png"] and
            sub_mimetype == self.mimes["svg"] and
            not self.exists(filename)
        ):
            # Remove extra ".png" extension
            filename = sub_filename
            svg_to_png = True

        encoded_filename = urllib.quote(filename)

        asset = self.swift_connection.get_object(
            self.container_name,
            encoded_filename
        )
        asset_data = asset[1]

        # Convert to png (if applicable)
        if svg_to_png:
            with Image(
                blob=asset_data,
                format="svg"
            ) as image:
                asset_data = image.make_blob("png")

        return asset_data

    def delete(self, filename):
        self.swift_connection.delete_object(
            self.container_name,
            urllib.quote(filename)
        )
        return True

    def generate_asset_filename(self, file_data, filename):
        """
        Generate a unique asset filename
        based on the old filename
        """

        return '{0}-{1}'.format(
            sha1(file_data).hexdigest()[:8],
            filename
        )


class DataManager:
    """
    Generate data objects for assets
    """

    request = None
    data_collection = None

    def __init__(self, data_collection):
        self.data_collection = data_collection

    def update(self, filename, tags):
        search = {"filename": filename}

        data = {
            "filename": filename,
            "tags": tags
        }

        self.data_collection.update(search, data, True)

        return self.fetch_one(filename)

    def fetch_one(self, filename):
        asset_data = self.data_collection.find_one(
            {"filename": filename}
        )

        return self.format(asset_data) if asset_data else None

    def find(self, query):
        match = re.compile(query)

        results = self.data_collection.find(
            {
                '$or': [
                    {'filename': match},
                    {'tags': match}
                ]
            }
        )

        return [
            self.format(asset_data)
            for asset_data in results
        ]

    def exists(self, filename):
        return bool(self.fetch_one(filename))

    def format(self, asset_record):
        asset_data = {
            'filename': asset_record['filename'],
            'tags': asset_record["tags"] or "",
            'created': asset_record["_id"].generation_time.ctime()
        }

        mimetype = mimetypes.guess_type(asset_data['filename'])[0]

        if mimetype == "image/svg+xml":
            asset_data['png_filename'] = asset_data['filename'] + ".png"

        return asset_data

    def fetch(self, filenames):
        return [
            self.fetch_one(filename)
            for filename in filenames
        ]

    def delete(self, filename):
        self.data_collection.remove({'filename': filename})


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
