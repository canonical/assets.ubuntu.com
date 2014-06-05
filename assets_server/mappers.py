import re
import mimetypes
import urllib

from wand.image import Image
from hashlib import sha1
from swiftclient.client import ClientException as SwiftException

from models import Asset


class AssetManager:
    """
    Manage assets and data
    """

    file_manager = None
    data_manager = None

    def __init__(self, file_manager, data_manager):
        self.file_manager = file_manager
        self.data_manager = data_manager

    def create(self, file_stream, extra_data):
        """
        Create asset file and data
        """

        filename = self.file_manager.create(file_stream)
        return self.data_manager.update(filename, extra_data)

    def delete(self, filename):
        """
        Delete file and data for asset
        """

        self.file_manager.delete(filename)
        self.data_manager.delete(filename)

    def find(self, queries):
        for query in queries:
            pass


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

    def format(self, asset_data):
        asset = Asset(
            filename=asset_data['filename'],
            tags=asset_data["tags"],
            created=asset_data["_id"].generation_time.ctime()
        )

        mimetype = mimetypes.guess_type(asset.filename)[0]

        if mimetype == "image/svg+xml":
            asset.png_filename = asset.filename + ".png"

        return asset

    def fetch(self, filenames):
        return [
            self.fetch_one(filename)
            for filename in filenames
        ]
