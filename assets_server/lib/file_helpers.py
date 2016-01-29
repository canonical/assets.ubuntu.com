# System
import errno
import mimetypes
import re

# Packages
from django.conf import settings

# Local
from processors import ImageProcessor


def create_asset(
    file_data, friendly_name, tags='', url_path='', optimize=False
):
    if optimize:
        image = ImageProcessor(file_data)
        image.optimize(allow_svg_errors=True)
        file_data = image.data

    if not url_path:
        url_path = settings.FILE_MANAGER.generate_asset_path(
            file_data,
            friendly_name
        )

    if settings.DATA_MANAGER.exists(url_path):
        raise file_error(
            error_number=errno.EEXIST,
            message="Asset already exists at {0}".format(url_path),
            filename=url_path
        )

    # Create file
    settings.FILE_MANAGER.create(file_data, url_path)

    # Once the file is created, create file metadata
    settings.DATA_MANAGER.update(url_path, tags)

    return url_path


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

    if is_hex(filename[:8]) and filename[8] == '-':
        filename = filename[9:]

    return filename


def get_mimetype(filename):
    """
    Get mimetype by file extension.
    If we have set an explicit mimetype, use that,
    otherwise ask Python to guess.
    """

    extra_mappings = {
        'woff2': 'font/woff2'
    }

    extension = re.search(r"(?<=\.)[^.]+$", filename).group(0)

    mime = extra_mappings.get(extension)

    if not mime:
        mime = mimetypes.guess_type(filename)[0]

    return mime


def file_error(error_number, message, filename):
    """
    Create an IOError
    """

    file_error = IOError(
        error_number,
        message
    )
    file_error.message = message
    file_error.filename = filename

    return file_error
