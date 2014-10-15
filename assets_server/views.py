# System
import os
import mimetypes
import errno
from io import BytesIO

# Packages
from django.http import HttpResponse, Http404
from django.conf import settings
from pilbox.errors import PilboxError
from swiftclient.client import (
    Connection as SwiftConnection,
    ClientException as SwiftClientException
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

# Local
from lib.processors import image_processor
from lib.http_helpers import error_response, file_from_base64
from auth import token_authorization
from mappers import FileManager, DataManager, DelayedConnection


# Managers
# ===
data_manager = DataManager(settings.MONGO_DB["asset_data"])
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

    @token_authorization
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

    @token_authorization
    def put(self, request, filename):
        """
        Update metadata against an asset
        """

        tags = request.DATA.get('tags', '')

        data = data_manager.update(filename, tags)

        return Response(data)


class AssetList(APIView):
    """
    Actions on the asset collection.
    """

    base_name = 'asset_list'

    @token_authorization
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

    @token_authorization
    def post(self, request):
        """
        Create a new asset
        """

        tags = request.DATA.get('tags', '')

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


class AssetJson(APIView):
    """
    Data about an asset
    """

    base_name = 'asset_json'

    @token_authorization
    def get(self, request, filename):
        """
        Get data for an asset by filename
        """

        return Response(data_manager.fetch_one(filename))


class Tokens(APIView):
    """
    HTTP methods for managing the collection of authentication tokens
    """

    @token_authorization
    def get(self, request):
        """
        Get data for an asset by filename
        """

        return Response(settings.TOKEN_MANAGER.all())

    @token_authorization
    def post(self, request):
        """
        Update metadata against an asset
        """

        name = request.DATA.get('name')
        body = {'name': name}
        token = False

        if not name:
            raise ParseError('To create a token, please specify a name')

        elif settings.TOKEN_MANAGER.exists(name):
            raise ParseError('Another token by that name already exists')

        else:
            token = settings.TOKEN_MANAGER.create(name)

            if token:
                body['message'] = 'Token created'
                body['token'] = token['token']
            else:
                raise ParseError('Failed to create a token')

        return Response(body)


class Token(APIView):
    """
    HTTP methods for managing a single authentication token
    """

    @token_authorization
    def get(self, request, name):
        """
        Get token data by name
        """

        token = settings.TOKEN_MANAGER.fetch(name)

        if not token:
            raise Http404

        return Response(token)

    @token_authorization
    def delete(self, request, name):
        """
        Delete a single named authentication token, 204 if successful
        """

        status = 200

        body = settings.TOKEN_MANAGER.delete(name) or {}

        if body:
            body['message'] = "Successfully deleted."
        else:
            raise Http404

        return Response(body, status)
