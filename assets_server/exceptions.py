from rest_framework.exceptions import AuthenticationFailed

class PrettyAuthenticationFailed(AuthenticationFailed):
    """
    A fork of the djangorestframework AuthenticationFailed exception
    to simply allow the `detail` parameter to contain fully formed
    JSON objects, rather than just text
    """

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = force_text(self.default_detail)
