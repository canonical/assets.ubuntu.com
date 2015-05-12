# System
from base64 import b64decode
from datetime import datetime
from urllib import unquote
import errno
import mimetypes
import os

# Packages
from django.conf import settings
from django.http import (
    HttpResponse, HttpResponseNotModified, HttpResponsePermanentRedirect
)
from pilbox.errors import PilboxError
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from swiftclient.exceptions import ClientException as SwiftClientException
import magic

# Local
from auth import token_authorization
from lib.file_helpers import create_asset, file_error, remove_filename_hash
from lib.http_helpers import error_response, error_404
from lib.processors import ImageProcessor


class Asset(APIView):
    """
    Actions on a single asset respource.
    """

    base_name = 'asset'

    def get(self, request, file_path):
        """
        Get a single asset, 404ing if we get an OSError.
        """

        try:
            asset_data = settings.FILE_MANAGER.fetch(file_path)
            asset_headers = settings.FILE_MANAGER.headers(file_path)
        except SwiftClientException as error:
            return error_response(error, file_path)

        time_format = '%a, %d %b %Y %H:%M:%S %Z'
        make_datetime = lambda x: datetime.strptime(x, time_format)
        last_modified = asset_headers['last-modified']
        if_modified_since = request.META.get(
            'HTTP_IF_MODIFIED_SINCE',
            'Mon, 1 Jan 1980 00:00:00 GMT'
        )

        if make_datetime(last_modified) <= make_datetime(if_modified_since):
            return HttpResponseNotModified()

        # Run image processor
        try:
            image = ImageProcessor(
                asset_data,
                request.GET
            )
            converted_type = image.process()
            asset_data = image.data
        except (PilboxError, ValueError) as error:
            return error_response(error, file_path)

        # Get a sensible filename, including a converted extension
        filename = remove_filename_hash(file_path)
        if converted_type:
            filename = '{0}.{1}'.format(filename, converted_type)

        # Start response, guessing mime type
        response = HttpResponse(
            asset_data,
            content_type=mimetypes.guess_type(filename)[0]
        )

        # Set download filename
        response['Content-Disposition'] = "filename={}".format(filename)

        # Cache all genuine assets forever
        response['Cache-Control'] = 'max-age=31556926'
        response['Last-Modified'] = last_modified

        # Return asset
        return response

    @token_authorization
    def delete(self, request, file_path):
        """
        Delete a single named asset, 204 if successful
        """

        try:
            settings.DATA_MANAGER.delete(file_path)
            settings.FILE_MANAGER.delete(file_path)
            return Response({"message": "Deleted {0}".format(file_path)})

        except SwiftClientException as err:
            return error_response(err, file_path)

    @token_authorization
    def put(self, request, file_path):
        """
        Update metadata against an asset
        """

        tags = request.DATA.get('tags', '')

        data = settings.DATA_MANAGER.update(file_path, tags)

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

        return Response(
            settings.DATA_MANAGER.find(regex_string),
            headers={'Cache-Control': 'no-cache'}
        )

    @token_authorization
    def post(self, request):
        """
        Create a new asset
        """

        tags = request.DATA.get('tags', '')
        optimize = request.DATA.get('optimize', False)
        asset = request.DATA.get('asset')
        friendly_name = request.DATA.get('friendly-name')
        url_path = request.DATA.get('url-path', '').strip('/')

        try:
            url_path = create_asset(
                file_data=b64decode(asset),
                friendly_name=friendly_name,
                tags=tags,
                url_path=url_path,
                optimize=optimize
            )
        except IOError as create_error:
            if create_error.errno == errno.EEXIST:
                return error_response(create_error)
            else:
                raise create_error
        except SwiftClientException as swift_error:
            return error_response(swift_error, url_path)

        # Return the list of data for the created files
        return Response(settings.DATA_MANAGER.fetch_one(url_path), 201)


class AssetInfo(APIView):
    """
    Data about an asset
    """

    base_name = 'asset_json'

    @token_authorization
    def get(self, request, file_path):
        """
        Get data for an asset by path
        """

        if settings.DATA_MANAGER.exists(file_path):
            response = Response(
                settings.DATA_MANAGER.fetch_one(file_path),
                headers={'Cache-Control': 'no-cache'}
            )
        else:
            asset_error = file_error(
                error_number=errno.ENOENT,
                message="No JSON data found for file {0}".format(file_path),
                filename=file_path
            )
            response = error_response(asset_error)

        return response


class Tokens(APIView):
    """
    HTTP methods for managing the collection of authentication tokens
    """

    @token_authorization
    def get(self, request):
        """
        Get a list of tokens
        """

        return Response(
            settings.TOKEN_MANAGER.all(),
            headers={'Cache-Control': 'no-cache'}
        )

    @token_authorization
    def post(self, request):
        """
        Create a new token
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
            return error_404(request.path)

        return Response(token)

    @token_authorization
    def delete(self, request, name):
        """
        Delete a single named authentication token, 204 if successful
        """

        body = settings.TOKEN_MANAGER.delete(name) or {}

        if body:
            body['message'] = "Successfully deleted."
        else:
            return error_404(request.path)

        return Response(body, 204)


class RedirectRecords(APIView):
    """
    HTTP methods for managing the collection of redirect records
    """

    @token_authorization
    def get(self, request):
        """
        Get data for a redirect by path
        """

        return Response(
            settings.REDIRECT_MANAGER.all(),
            headers={'Cache-Control': 'no-cache'}
        )

    @token_authorization
    def post(self, request):
        """
        Create a redirect record
        """

        redirect_path = request.DATA.get('redirect_path')
        target_url = request.DATA.get('target_url')

        body = {
            'redirect_path': redirect_path,
            'target_url': target_url
        }

        redirect_record = False

        if not redirect_path:
            raise ParseError(
                'To create a new redirect, please specify a '
                'redirect_path and a target_url'
            )

        elif settings.REDIRECT_MANAGER.exists(redirect_path):
            return Response(
                {
                    "message": 'Another redirect with that path already exists',
                    "redirect_path": redirect_path,
                    "code": 409
                },
                status=409
            )

        else:
            redirect_record = settings.REDIRECT_MANAGER.update(
                redirect_path,
                target_url
            )

            if redirect_record:
                body['message'] = 'Redirect created'
            else:
                raise ParseError('Failed to create redirect')

        return Response(body)


class RedirectRecord(APIView):
    """
    HTTP methods for managing a single redirect record
    """

    @token_authorization
    def get(self, request, redirect_path):
        """
        Get redirect data by name
        """

        redirect_record = settings.REDIRECT_MANAGER.fetch(
            unquote(redirect_path)
        )

        if not redirect_record:
            return error_404(request.path)

        return Response(redirect_record)

    @token_authorization
    def put(self, request, redirect_path):
        """
        Update target URL for a redirect
        """

        target_url = request.DATA.get('target_url')

        if not target_url:
            raise ParseError('To update a redirect, please supply a target_url')

        if target_url:
            redirect_record = settings.REDIRECT_MANAGER.update(
                unquote(redirect_path),
                target_url
            )

        return Response(redirect_record)

    @token_authorization
    def delete(self, request, redirect_path):
        """
        Delete a single redirect by its request URL path,
        204 if successful
        """

        body = settings.REDIRECT_MANAGER.delete(unquote(redirect_path)) or {}

        if body:
            body['message'] = "Successfully deleted."
        else:
            return error_404(request.path)

        return Response(body, 204)


class Redirects(APIView):
    """
    Do 301 redirect for any redirects found in the MongoDB
    """

    def get(self, request, request_path):
        redirect_record = settings.REDIRECT_MANAGER.fetch(request_path)

        if not redirect_record:
            return error_404(request.path)

        return HttpResponsePermanentRedirect(redirect_record['target_url'])
