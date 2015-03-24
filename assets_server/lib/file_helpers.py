# System
import errno

# Packages
from django.conf import settings

# Local
from processors import ImageProcessor


def create_asset(
    file_data, friendly_name, tags='', url_path='', optimize=False
):
    if optimize:
        image = ImageProcessor(file_data)
        image.optimize()
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
