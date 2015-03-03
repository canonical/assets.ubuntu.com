from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.http.multipartparser import parse_header

def unparse_header(base_setting, params):
    output_string = base_setting

    for key, value in params.iteritems():
        output_string += '; {0}={1}'.format(key, value)

    return output_string

class PrettyJSONRenderer(JSONRenderer):
    """
    Extend the existing JSONRenderer from djangorestframework
    by using settings.DEFAULT_JSON_INDENT
    to always pretty-print JSON output
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if hasattr(settings, 'DEFAULT_JSON_INDENT'):
            if accepted_media_type:
                base_media_type, params = parse_header(accepted_media_type.encode('ascii'))
                if not params.get('indent'):
                    params['indent'] = settings.DEFAULT_JSON_INDENT
                    accepted_media_type = unparse_header(base_media_type, params)
            else:
                accepted_media_type = 'application/json; indent=4'

        return super(PrettyJSONRenderer, self).render(data, accepted_media_type, renderer_context)
