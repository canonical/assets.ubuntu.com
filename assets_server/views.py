# System
import os
import mimetypes
import errno
from io import BytesIO
from base64 import b64decode

# Packages
from django.http import HttpResponse, Http404
from django.conf import settings
from pilbox.errors import PilboxError
from swiftclient.client import Connection as SwiftConnection
from swiftclient.exceptions import ClientException as SwiftClientException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

# Local
from lib.processors import image_processor
from lib.http_helpers import error_response
from auth import token_authorization
from mappers import FileManager, DataManager


# Managers
# ===
data_manager = DataManager(data_collection=settings.MONGO_DB['asset_data'])
file_manager = FileManager(
    SwiftConnection(
        os.environ.get('OS_AUTH_URL'),
        os.environ.get('OS_USERNAME'),
        os.environ.get('OS_PASSWORD'),
        auth_version='2.0',
        os_options={'tenant_name': os.environ.get('OS_TENANT_NAME')}
    )
)


class Asset(APIView):
    """
    Actions on a single asset respource.
    """

    base_name = 'asset'

    def get(self, request, file_path):
        """
        Get a single asset, 404ing if we get an OSError.
        """

        mimetype = mimetypes.guess_type(file_path)[0]

        try:
            asset_stream = BytesIO(file_manager.fetch(file_path))
        except SwiftClientException as error:
            return error_response(error, file_path)

        image_types = ["image/png", "image/jpeg"]

        # Run images through processor
        if request.GET and mimetype in image_types:
            try:
                asset_stream = image_processor(
                    asset_stream,
                    request.GET
                )
            except PilboxError as error:
                return error_response(error, file_path)

        # Return asset
        return HttpResponse(asset_stream.read(), mimetype)

    @token_authorization
    def delete(self, request, file_path):
        """
        Delete a single named asset, 204 if successful
        """

        try:
            data_manager.delete(file_path)
            file_manager.delete(file_path)
            return Response({"message": "Deleted {0}".format(file_path)})

        except SwiftClientException as err:
            return error_response(err, file_path)

    @token_authorization
    def put(self, request, file_path):
        """
        Update metadata against an asset
        """

        tags = request.DATA.get('tags', '')

        data = data_manager.update(file_path, tags)

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
        file paths
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
        asset = request.DATA.get('asset')
        friendly_name = request.DATA.get('friendly-name')
        url_path = request.DATA.get('url-path', '').strip('/')

        # Get file data
        file_data = b64decode(asset)

        # Generate the asset path
        if not url_path:
            url_path = file_manager.generate_asset_path(
                file_data,
                friendly_name
            )

        # Error if it exists
        if data_manager.exists(url_path):
            return error_response(
                IOError(
                    errno.EEXIST,
                    "Asset already exists",
                    url_path
                )
            )

        try:
            # Create file
            file_manager.create(file_data, url_path)
        except SwiftClientException as error:
            return error_response(error, url_path)

        # Once the file is created, create file metadata
        data_manager.update(url_path, tags)

        # Return the list of data for the created files
        return Response(data_manager.fetch_one(url_path), 201)


class AssetJson(APIView):
    """
    Data about an asset
    """

    base_name = 'asset_json'

    @token_authorization
    def get(self, request, file_path):
        """
        Get data for an asset by path
        """

        return Response(data_manager.fetch_one(file_path))


class Tokens(APIView):
    """
    HTTP methods for managing the collection of authentication tokens
    """

    @token_authorization
    def get(self, request):
        """
        Get data for an asset by path
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
