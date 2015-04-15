import urllib


def normalize(url_to_normalize):
    """
    Given a URL, it will unquote it and requote it
    with "quote_plus" so that spaces become "+"
    """

    unquoted_url = urllib.unquote_plus(url_to_normalize)
    requoted_url = urllib.quote_plus(unquoted_url)
    return requoted_url
