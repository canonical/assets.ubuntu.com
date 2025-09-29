# trino_client.py
import logging
from typing import Optional
import trino.auth
from trino.dbapi import connect
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from webapp.config import config

logger = logging.getLogger(__name__)


class TrinoClient:
    def __init__(self):
        self.scopes = ["openid", "email"]
        self._request = Request()

    def _get_token(self) -> Optional[str]:
        try:
            service_account_dict = config.trino_sf.model_dump()
            credentials = service_account.Credentials.from_service_account_info(
                service_account_dict,
                scopes=self.scopes,
            )
            credentials.refresh(self._request)
            return credentials.token
        except Exception:
            logger.exception(
                "Unable to refresh Trino service account token: ", Exception
            )
            return None

    def get_cursor(self):
        token = self._get_token()
        if not token:
            return None
        conn = connect(
            host="candidate.trino.canonical.com",
            port=443,
            http_scheme="https",
            auth=trino.auth.JWTAuthentication(token),
            verify=True,
            catalog="salesforce",
            schema="canonical",
        )
        return conn.cursor()


trino_client = TrinoClient()
trino_cur = trino_client.get_cursor()
