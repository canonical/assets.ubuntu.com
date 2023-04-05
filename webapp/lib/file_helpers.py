import mimetypes
import os
import re

import filetype


def is_hex(hex_string):
    """
    Check if a string is hexadecimal
    """

    try:
        int(hex_string, 16)
        return True
    except ValueError:
        return False


def remove_filename_hash(filename):
    """
    Remove the 8-digit unique hexadecimal hash
    from a filename
    """

    if is_hex(filename[:8]) and filename[8] == "-":
        filename = filename[9:]

    return filename


def get_mimetype(filepath):
    """
    Get mimetype by file extension.
    If we have set an explicit mimetype, use that,
    otherwise ask Python to guess.
    """

    mappings = {".woff2": "font/woff2"}

    extension = os.path.splitext(filepath)[1]

    return mappings.get(extension) or mimetypes.guess_type(filepath)[0]


SVG_R = r"(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b"
SVG_RE = re.compile(SVG_R, re.DOTALL)


def is_svg(data):
    content = data.decode("latin_1")
    return SVG_RE.match(content) is not None


def guess_mime(data):
    """
    Get the mimetype of the data.
    This is intented to mainly handle guess image types.
    args:
    - data: bytes of data
    returns:
    The mimetype: image/png, image/jpeg, image/svg+xml... or None
    """

    mimetype = filetype.guess_mime(data)
    # filetype.guess_mime only supports binary content
    if not mimetype and is_svg(data):
        return "image/svg+xml"
    return mimetype
