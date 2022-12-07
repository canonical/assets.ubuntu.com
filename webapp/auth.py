from webapp.database import db_session
from webapp.models import Token


def authenticate(token):
    """Check if this authentication token is valid (i.e. exists)"""

    return bool(
        db_session.query(Token).filter(Token.token == token).one_or_none()
    )
