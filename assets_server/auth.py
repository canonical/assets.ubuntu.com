from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


def token_authorization(target_function):
    """
    Decorator for view methods to force token authentication
    Makes sure that the supplied token exists in mongodb
    """

    def inner(self, request, *args, **kwargs):
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
            raise AuthenticationFailed
        return target_function(self, request, *args, **kwargs)
    return inner
