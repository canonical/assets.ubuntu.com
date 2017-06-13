from rest_framework.renderers import JSONRenderer
from django.conf import settings


class PrettyJSONRenderer(JSONRenderer):
    """
    Extend the existing JSONRenderer from djangorestframework
    by using settings.DEFAULT_JSON_INDENT
    to always pretty-print JSON output
    """

    def get_indent(self, accepted_media_type, renderer_context):
        if (
            hasattr(settings, 'DEFAULT_JSON_INDENT') and
            not renderer_context.get('indent')
        ):
            renderer_context['indent'] = settings.DEFAULT_JSON_INDENT

        return super(PrettyJSONRenderer, self).get_indent(
            accepted_media_type,
            renderer_context
        )
