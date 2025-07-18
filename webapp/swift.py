# Standard library
from hashlib import sha1
from typing import Optional

# Packages
import swiftclient
import swiftclient.exceptions
from swiftclient.exceptions import ClientException as SwiftException

# Local
from webapp.config import config
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
    swift_connection: swiftclient.client.Connection

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

    def exists(self, file_path: str) -> bool:
        file_exists = True

        try:
            self.swift_connection.head_object(
                self.container_name, normalize(file_path)
            )
        except SwiftException as error:
            if error.http_status == 404:
                file_exists = False

        return file_exists

    def fetch(self, file_path: str) -> Optional[bytes]:
        try:
            asset = self.swift_connection.get_object(
                self.container_name, normalize(file_path)
            )
            return asset[1]
        except swiftclient.exceptions.ClientException as error:
            if error.http_status == 404:
                return None
            raise error

    def headers(self, file_path: str) -> dict:
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
    config.swift.auth_url,
    config.swift.username,
    config.swift.password.get_secret_value(),
    auth_version=config.swift.auth_version,
    os_options={"tenant_name": config.swift.tenant_name},
)

file_manager = FileManager(swift_connection)
