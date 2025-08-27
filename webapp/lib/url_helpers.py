import re
import os

try:
    from urllib.parse import quote_plus, unquote_plus
except ImportError:
    from urllib import quote_plus, unquote_plus


def normalize(url_to_normalize):
    """
    Given a URL, it will unquote it and requote it
    with "quote_plus" so that spaces become "+"
    """

    unquoted_url = unquote_plus(url_to_normalize)
    requoted_url = quote_plus(unquoted_url)
    return requoted_url


def sanitize_filename(file_name: str) -> str:
    """
    Sanitize file names:
    - Keeps A-Z, a-z, 0-9
    - Removes spaces
    - Replaces any other character with '_'
    - Preserves the last '.' before the extension
    """
    if not file_name:
        return ""

    base, ext = os.path.splitext(file_name)

    sanitized_base = re.sub(r"[^A-Za-z0-9]", "_", base)
    sanitized_base = re.sub(r"_+", "_", sanitized_base)  # collapse multiple _
    sanitized_base = sanitized_base.strip("_")           # remove leading/trailing _

    return f"{sanitized_base}{ext}"