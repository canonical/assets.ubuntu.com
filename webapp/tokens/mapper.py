import uuid

from webapp.alembic.env import get_database_session
from webapp.models import Token


database_session = get_database_session()


def create_token(name):
    """Generate a random token, with a given name"""
    token = Token(name=name, token=uuid.uuid4().hex)
    database_session.add(token)
    database_session.commit()

    return token


def delete_token_by_name(name):
    """Delete a token"""
    token = find_token_by_name(name)

    if not token:
        return None

    database_session.delete(token)
    database_session.commit()

    return True


def find_token(token_str):
    """Get a token"""
    token = (
        database_session.query(Token)
        .filter(Token.token == token_str)
        .one_or_none()
    )
    return token


def find_token_by_name(name):
    """Get a token by its name"""
    token = (
        database_session.query(Token).filter(Token.name == name).one_or_none()
    )
    return token


def get_all_tokens():
    """Get all tokens"""
    return database_session.query(Token).all()
