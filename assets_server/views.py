# System
import os
import mimetypes
import errno
from io import BytesIO

# Packages
from django.http import HttpResponse
from pilbox.errors import PilboxError
from pymongo import MongoClient
from swiftclient.client import (
    Connection as SwiftConnection,
    ClientException as SwiftClientException
)
from rest_framework.views import APIView
from rest_framework.response import Response

# Local
from lib.processors import image_processor
from lib.http_helpers import error_response, file_from_base64
from mappers import FileManager, DataManager, DelayedConnection


# MongoDB settings
# ===
mongo_url = os.environ.get('DATABASE_URL', 'mongodb://localhost/')
mongo_client = MongoClient(mongo_url)
mongo_collection = mongo_client["assets"]["asset_data"]
data_manager = DataManager(data_collection=mongo_collection)
mongo_connected = True

# Setup file_manager with swift
# ===
swift = DelayedConnection(
    manager_class=FileManager,
    connection_class=SwiftConnection,
    auth_url=os.environ.get('OS_AUTH_URL'),
    username=os.environ.get('OS_USERNAME'),
    password=os.environ.get('OS_PASSWORD'),
    auth_version='2.0',
    tenant_name=os.environ.get('OS_TENANT_NAME')
)


class Asset(APIView):
    """
    Actions on a single asset respource.
    """

    base_name = 'asset'

    def get(self, request, filename):
        """
        Get a single asset, 404ing if we get an OSError.
        """

        mimetype = mimetypes.guess_type(filename)[0]

        try:
            asset_stream = BytesIO(swift.manager().fetch(filename))
        except SwiftClientException as error:
            return error_response(error, filename)

        image_types = ["image/png", "image/jpeg"]

        # Run images through processor
        if request.GET and mimetype in image_types:
            try:
                asset_stream = image_processor(
                    asset_stream,
                    request.GET
                )
            except PilboxError as error:
                return error_response(error, filename)

        # Return asset
        return HttpResponse(asset_stream.read(), mimetype)

    def delete(self, request, filename):
        """
        Delete a single named asset, 204 if successful
        """

        try:
            data_manager.delete(filename)
            swift.manager().delete(filename)
            return Response({"message": "Deleted {0}".format(filename)})

        except SwiftClientException as err:
            return error_response(err, filename)

    def put(self, request, filename):
        """
        Update metadata against an asset
        """

        tags = request.DATA.get('tags')

        data = data_manager.update(filename, tags)

        return Response(data)


class AssetList(APIView):
    """
    Actions on the asset collection.
    """

    base_name = 'asset_list'

    def post(self, request):
        """
        Create a new asset
        """

        tags = request.DATA.get('tags')

        # Get file data
        file_stream = file_from_base64(request, 'asset', 'filename')
        file_data = file_stream.read()
        file_manager = swift.manager()

        # Generate the asset filename
        filename = file_manager.generate_asset_filename(
            file_data,
            file_stream.filename
        )

        # Error if it exists
        if data_manager.exists(filename):
            return error_response(
                IOError(
                    errno.EEXIST,
                    "Asset already exists",
                    filename
                )
            )

        # Create file metadata
        data_manager.update(filename, tags)

        # Create file
        try:
            file_manager.create(file_data, filename)
        except SwiftClientException as error:
            return error_response(error, filename)

        # Return the list of data for the created files
        return Response(data_manager.fetch_one(filename), 201)

    def get(self, request):
        """
        Get all assets.

        Filter asset by providing a query
        /?q=<query>

        Query parts should be space separated,
        and results will match all parts

        Currently, the query will only be matched against
        filenames
        """

        queries = request.GET.get('q', '').split(' ')

        regex_string = '({0})'.format('|'.join(queries))

        return Response(data_manager.find(regex_string))


class AssetJson(APIView):
    """
    Data about an asset
    """

    base_name = 'asset_json'

    def get(self, request, filename):
        """
        Get data for an asset by filename
        """

        return Response(data_manager.fetch_one(filename))
