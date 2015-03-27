# Installed packages
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

# Local code
from views import Asset, AssetList, AssetInfo, Tokens, Token

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url='/v1/', permanent=False)),
    url(r'^v1/?$', AssetList.as_view()),
    url(r'^v1/tokens/?$', Tokens.as_view()),
    url(r'^v1/tokens/(?P<name>.+)$', Token.as_view()),
    url(r'^v1/(?P<file_path>.+)/info$', AssetInfo.as_view()),
    url(r'^v1/(?P<file_path>.+)$', Asset.as_view()),
)
