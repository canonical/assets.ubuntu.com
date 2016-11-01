# System
import errno
import mimetypes
import os
import re

# Packages
from django.conf import settings
from wand.image import Image

# Local
from processors import ImageProcessor


def create_asset(
    file_data, friendly_name, tags='', url_path='', optimize=False
):
    data = {"optimized": optimize}

    if optimize:
        try:
            image = ImageProcessor(file_data)
            image.optimize(allow_svg_errors=True)
            file_data = image.data
        except:
            # If optimisation failed, just don't bother optimising
            data["optimized"] = "Optimization failed"

    if not url_path:
        url_path = settings.FILE_MANAGER.generate_asset_path(
            file_data,
            friendly_name
        )

    try:
        with Image(blob=file_data) as image_info:
            data['width'] = image_info.width
            data['height'] = image_info.height
    except:
        # Just don't worry if image reading fails
        pass

    # Create file
    if not settings.DATA_MANAGER.exists(url_path):
        try:
            settings.FILE_MANAGER.create(file_data, url_path)
        except:
            raise file_error(
                error_number=errno.EEXIST,
                message="Failed to create asset {0}.".format(url_path),
                filename=url_path
            )
    else:
        error_message = "Asset already exists at {0}.".format(url_path)
        asset = settings.DATA_MANAGER.fetch_one(url_path)

        image_data = {}

        if "width" not in asset and "width" in data:
            image_data["width"] = data["width"]

        if "height" not in asset and "height" in data:
            image_data["height"] = data["height"]

        if image_data:
            settings.DATA_MANAGER.update(url_path, asset['tags'], image_data)
            error_message += " Updated image information."

        raise file_error(
            error_number=errno.EEXIST,
            message=error_message,
            filename=url_path
        )

    # Once the file is created, create file metadata
    settings.DATA_MANAGER.update(url_path, tags, data)

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


def get_mimetype(filepath):
    """
    Get mimetype by file extension.
    If we have set an explicit mimetype, use that,
    otherwise ask Python to guess.
    """

    mappings = {
        '.woff2': 'font/woff2'
    }

    extension = os.path.splitext(filepath)[1]

    return mappings.get(extension) or mimetypes.guess_type(filepath)[0]


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
