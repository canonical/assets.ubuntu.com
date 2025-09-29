from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def shared_items(list_one, list_two):
    """
    Return the list of items that are shared
    between two lists
    """

    return [x for x in list_one.keys() if x in list_two]


def sanitize_like_input(raw: str) -> str:
    """Escape special characters used in SQL LIKE"""
    escaped = raw.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return escaped


def is_pem_private_key(data: bytes) -> bool:
    """
    Return True if the given data is a valid PEM private key.
    """
    try:
        serialization.load_pem_private_key(
            data, password=None, backend=default_backend()
        )
        return True
    except Exception:
        return False
