import errno
from rest_framework.response import Response


def error_response(error, file_path=''):
    """
    Given an IO error,
    generate the correct HTTP and JSON response:

    403: EPERM, EACCES
    404: ENOENT, ENXIO
    409: EEXIST
    413: E2BIG
    500: Anything else
    """

    status = 500  # Default to "server error"
    file_path = file_path or error.filename

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
            "file_path": file_path,
            "error_class": error.__class__.__name__,
            "message": message,
            "code": status
        },
        status=status
    )
