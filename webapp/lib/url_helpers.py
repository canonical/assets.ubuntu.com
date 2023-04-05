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


def clean_unicode(file_name):
    """
    Given a file name, it will remove any unicode characters
    that are not supported by the filesystem.
    """
    if file_name:
        return file_name.encode("latin-1", "ignore").decode("latin-1")
