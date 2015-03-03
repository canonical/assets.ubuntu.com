from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework.exceptions import AuthenticationFailed
from assets_server.exceptions import PrettyAuthenticationFailed
from rest_framework.renderers import JSONRenderer, YAMLRenderer


def token_authorization(target_function):
    """
    Decorator for view methods to force token authentication
    Makes sure that the supplied token exists in mongodb
    """

    def inner(self, request, *args, **kwargs):
        # API calls have to be over HTTPS
        # So if both DEBUG and the request wasn't https, we should redirect

        # This detects if the request was through a secure front-end
        forwarded_protocol = request.META.get('HTTP_X_FORWARDED_PROTO', '')
        is_secure = request.is_secure() or forwarded_protocol == 'https'

        if not (settings.DEBUG or is_secure):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponseRedirect(secure_url)

        # HTTP authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        # Combine request parameters
        params = request.GET.dict()
        params.update(request.DATA.dict())

        # Token based authorization
        if auth_header[:6].lower() == "token ":
            token = auth_header[6:]
        else:
            token = params.get('token')

        if not settings.TOKEN_MANAGER.authenticate(token):
            message = 'Unauthorized: Please provide a valid API token.'

            renderer_classes = (JSONRenderer, )

            if token and token.replace(' ', '').lower() == 'correcthorsebatterystaple':
                with open('correct.txt') as correct_file:
                    message = correct_file.read().splitlines()

            raise PrettyAuthenticationFailed(
                detail=message
            )
        return target_function(self, request, *args, **kwargs)
    return inner
