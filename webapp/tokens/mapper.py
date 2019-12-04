import uuid

from webapp.database import db
from webapp.models import Token


def create_token(name):
    """Generate a random token, with a given name"""
    token = Token(name=name, token=uuid.uuid4().hex)
    db.add(token)
    db.commit()

    return token


def delete_token_by_name(name):
    """Delete a token"""
    token = find_token_by_name(name)

    if not token:
        return None

    db.delete(token)
    db.commit()

    return True


def find_token(token_str):
    """Get a token"""
    token = db.query(Token).filter(Token.token == token_str).one_or_none()
    return token


def find_token_by_name(name):
    """Get a token by its name"""
    token = db.query(Token).filter(Token.name == name).one_or_none()
    return token


def get_all_tokens():
    """Get all tokens"""
    return db.query(Token).all()
