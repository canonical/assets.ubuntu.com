def set_headers_for_type(response, content_type=None):
    """
    Setup all requires response headers appropriate for this file
    """

    if not content_type:
        content_type = response.headers["Content-Type"]

    if "font" in content_type:
        response.headers["Access-Control-Allow-Origin"] = "*"

    return response
