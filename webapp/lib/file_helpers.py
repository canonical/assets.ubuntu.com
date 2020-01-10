# System
import mimetypes
import os


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


def file_error(error_number, message, filename):
    """
    Create an IOError
    """

    file_error = IOError(error_number, message)
    file_error.message = message
    file_error.filename = filename

    return file_error
