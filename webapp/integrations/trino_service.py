# trino_client.py
import logging
import sys
from typing import Optional
import trino.auth
from trino.dbapi import connect
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from webapp.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

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
        except Exception as e:
            logger.exception("Unable to refresh Trino service account token: %s", e)
            return None

    def get_cursor(self):
        token = self._get_token()
        if not token:
            return None
        try:
            conn = connect(
                host=config.trino_sf.host,
                port=config.trino_sf.connection_port,
                http_scheme=config.trino_sf.http_scheme,
                auth=trino.auth.JWTAuthentication(token),
                verify=True,
                catalog=config.trino_sf.catalog,
                schema=config.trino_sf.schema,
            )
            return conn.cursor()
        except Exception as e:
            logger.exception("Unable to connect to Trino: %s", e)
            return None


trino_client = TrinoClient()
trino_cur = trino_client.get_cursor()
