import logging
import sys

import trino.auth
from webapp.config import config
from google.auth.transport import requests
from google.oauth2 import service_account
from trino.dbapi import connect


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_service_account_token():
    try:
        trino_service_account = config.trino_sf
        service_account_dict = trino_service_account.model_dump()
        credentials = service_account.Credentials.from_service_account_info(
            service_account_dict, scopes=["openid", "email"]
        )
        credentials.refresh(requests.Request())
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to load Trino configuration: {e}")
        return None


# Prepare the trino connection using the service account token
token = get_service_account_token()
if not token:
    logger.error("Failed to obtain service account token.")
else:
    trino_conn = connect(
        host="candidate.trino.canonical.com",
        port=443,
        http_scheme="https",
        auth=trino.auth.JWTAuthentication(token),
        verify=True,
        catalog="salesforce",
        schema="canonical",
    )
    trino_cur = trino_conn.cursor()
