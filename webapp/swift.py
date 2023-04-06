# Standard library
import os
from hashlib import sha1

# Packages
import swiftclient
from swiftclient.exceptions import ClientException as SwiftException

# Local
from webapp.lib.url_helpers import normalize


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
                self.container_name, normalize(file_path), file_data
            )
        except SwiftException as swift_error:
            if swift_error.http_status != 404:
                raise swift_error

            # Not found, assuming container doesn't exist
            self.swift_connection.put_container(self.container_name)

            # And try to create again
            self.swift_connection.put_object(
                self.container_name, normalize(file_path), file_data
            )

    def exists(self, file_path):
        file_exists = True

        try:
            self.swift_connection.head_object(
                self.container_name, normalize(file_path)
            )
        except SwiftException as error:
            if error.http_status == 404:
                file_exists = False

        return file_exists

    def fetch(self, file_path):
        asset = self.swift_connection.get_object(
            self.container_name, normalize(file_path)
        )
        return asset[1]

    def headers(self, file_path):
        return self.swift_connection.head_object(
            self.container_name, normalize(file_path)
        )

    def delete(self, file_path):
        if self.exists(file_path):
            self.swift_connection.delete_object(
                self.container_name, normalize(file_path)
            )
            return True

    def generate_asset_path(self, file_data, friendly_name):
        """
        Generate a unique asset file_path
        based on a friendly name
        """

        path = sha1(file_data).hexdigest()[:8]
        if friendly_name:
            path += "-" + friendly_name

        return path


swift_connection = swiftclient.client.Connection(
    os.environ.get("OS_AUTH_URL"),
    os.environ.get("OS_USERNAME"),
    os.environ.get("OS_PASSWORD"),
    auth_version=os.environ.get("OS_AUTH_VERSION", "2.0"),
    os_options={"tenant_name": os.environ.get("OS_TENANT_NAME")},
)

file_manager = FileManager(swift_connection)
