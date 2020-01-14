# System
import os
import errno

# Packages
from flask import jsonify


def content_404():
    """
    Render the 404 ASCII art as a nice array
    of strings, so it will render nicely in JSON
    """

    this_dir = os.path.dirname(os.path.realpath(__file__))
    app_dir = os.path.dirname(this_dir)
    chbs_art_path = "{0}/art/404.ascii".format(app_dir)

    with open(chbs_art_path) as chbs_file:
        return chbs_file.read().splitlines()


def error_response(error, file_path=""):
    """
    Given an IO error,
    generate the correct HTTP and JSON response:

    403: EPERM, EACCES
    404: ENOENT, ENXIO
    409: EEXIST
    413: E2BIG
    500: Anything else
    """
    # We need getattr here because SwiftErrors don't have a filename attr
    file_path = file_path or getattr(error, "filename", "unknow")

    # Get the status from either .errno or .http_status
    status = 500  # Default to "server error"

    if hasattr(error, "status_code"):
        status = error.status_code

    if hasattr(error, "errno"):
        if error.errno in [errno.EPERM, errno.EACCES]:
            status = 403  # Forbidden

        if error.errno in [errno.ENOENT, errno.ENXIO]:
            status = 404  # Not found

        if error.errno in [errno.EEXIST]:
            status = 409  # Conflict

        if error.errno in [errno.E2BIG]:
            status = 413  # Request Entity Too Large

    if hasattr(error, "http_status"):
        if error.http_status and error.http_status > 99:
            status = error.http_status
        elif hasattr(error, "msg") and error.msg[:12] == "Unauthorised":
            # Special case for swiftclient.exceptions.ClientException
            status = 511

    # Get the message from somewhere
    message = ""
    if hasattr(error, "msg") and error.msg:
        message = error.msg
    elif hasattr(error, "message") and error.message:
        message = error.message
    elif hasattr(error, "strerror") and error.strerror:
        message = error.strerror
    elif hasattr(error, "log_message") and error.log_message:
        message = error.log_message

    if status == 404:
        message = [message, ""]
        message += content_404()

    return (
        jsonify(
            {
                "message": message,
                "file_path": file_path,
                "error_class": error.__class__.__name__,
                "code": status,
            }
        ),
        status,
    )


def set_headers_for_type(response, content_type=None):
    """
    Setup all requires response headers appropriate for this file
    """

    if not content_type:
        content_type = response.headers["Content-Type"]

    if "font" in content_type:
        response.headers["Access-Control-Allow-Origin"] = "*"

    return response
