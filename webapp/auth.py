from webapp.tokens.mapper import find_token


def authenticate(token):
    """Check if this authentication token is valid (i.e. exists)"""
    return True if find_token(token) else False
