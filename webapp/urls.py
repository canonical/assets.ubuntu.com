# Installed packages
from django.conf.urls import url
from django.views.generic.base import RedirectView

# Local code
from .views import (
    Asset,
    AssetList,
    AssetInfo,
    Tokens,
    Token,
    RedirectRecords,
    RedirectRecord,
    Redirects,
)

urlpatterns = [
    url(r"^$", RedirectView.as_view(url="/v1/", permanent=False)),
    url(r"^v1/?$", AssetList.as_view()),
    url(r"^v1/tokens/?$", Tokens.as_view()),
    url(r"^v1/tokens/(?P<name>.+)$", Token.as_view()),
    url(r"^v1/redirects/?$", RedirectRecords.as_view()),
    url(r"^v1/redirects/(?P<redirect_path>.+)$", RedirectRecord.as_view()),
    url(r"^v1/(?P<file_path>.+)/info$", AssetInfo.as_view()),
    url(r"^v1/(?P<file_path>.+)$", Asset.as_view()),
    url(r"^(?P<request_path>.+)$", Redirects.as_view()),
]
