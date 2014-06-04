import errno
from io import BytesIO
from base64 import b64decode
from werkzeug.datastructures import FileStorage
from rest_framework.response import Response


def error_response(error, filename=''):
    status = 500  # Default to "server error"
    filename = filename or error.filename

    if hasattr(error, 'errno'):
        if error.errno in [errno.EPERM, errno.EACCES]:
            status = 403  # Forbidden

        if error.errno in [errno.ENOENT, errno.ENXIO]:
            status = 404  # Not found

        if error.errno in [errno.EEXIST]:
            status = 409  # Conflict

        if error.errno in [errno.E2BIG]:
            status = 413  # Request Entity Too Large

    if hasattr(error, 'http_status'):
        status = error.http_status

    message = error.message

    if not message and hasattr(error, "strerror"):
        message = error.strerror
    elif not message and hasattr(error, "log_message"):
        message = error.log_message

    return Response(
        {
            "filename": filename,
            "error_class": error.__class__.__name__,
            "message": message,
            "code": status
        },
        status=status
    )


def file_from_base64(request, file_key, filename_key):
    """
    Given a request containing a file submitted as base64 data
    e.g.:
        requests.post(
            url,
            data={
                '<key>': b64encode(file_data),
            }
        )
    Extract and return the file
    """

    file_object = None

    base64_file = request.DATA.get(file_key)
    filename = request.DATA.get(filename_key) or 'asset'

    if base64_file:
        file_data = b64decode(base64_file)
        file_object = FileStorage(
            stream=BytesIO(file_data),
            filename=filename
        )

    return file_object
