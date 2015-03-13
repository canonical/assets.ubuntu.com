from copy import deepcopy
from PIL import Image as PILImage
from pilbox.image import Image
from pilbox.errors import PilboxError


def catch_missing_param_error(error, operation_name, operation_params):
    expected_errors = [
        "int() argument must be a string or a number, not 'NoneType'",
        "'NoneType' object has no attribute 'split'"
    ]

    if error.message in expected_errors:
        message = "Image operation '{0}' requires one of: {1}".format(
            operation_name,
            ', '.join(operation_params)
        )

        raise PilboxError(400, log_message=message)
    else:
        raise error


def image_processor(image_stream, params):
    """
    Perform transformations on an image
    Using Pilbox: https://github.com/nottrobin/pilbox
    The params follow Pilbox's API
    """

    op = params.get("op")

    resize_operations = ['w', 'h', 'mode', 'filter', 'bg', 'pos']
    used_operations = [x for x in params.keys() if x in resize_operations]

    if op == "region":
        try:
            image = Image(image_stream)
            image.region(
                params.get("rect").split(',')
            )
        except AttributeError as region_error:
            catch_missing_param_error(region_error, 'rotate', ['rect'])

    elif op == "rotate":
        try:
            image = Image(image_stream)
            image.rotate(
                deg=params.get("deg"),
                expand=params.get("expand")
            )
        except TypeError as rotate_error:
            catch_missing_param_error(rotate_error, 'rotate', ['deg', 'expand'])
    elif op == "resize" or used_operations:
        resize_width = int(params.get("w")) if params.get("w") else None
        resize_height = int(params.get("h")) if params.get("h") else None

        if resize_width or resize_height:
            # Don't allow expanding of images
            image_stream_2 = deepcopy(image_stream)
            (width, height) = PILImage.open(image_stream_2).size

            if resize_width > width or resize_height > height:
                expand_message = (
                    "Resize error: Maximum dimensions for this image "
                    "are {0}px wide by {1}px high."
                ).format(width, height)

                raise PilboxError(
                    400,
                    log_message=expand_message
                )

        try:
            image = Image(image_stream)
            image.resize(
                width=resize_width,
                height=resize_height,
                mode=params.get("mode"),
                filter=params.get("filter"),
                background=params.get("bg"),
                position=params.get("pos")
            )
        except TypeError as resize_error:
            catch_missing_param_error(resize_error, 'resize', resize_operations)

    return image.save(
        format=params.get("fmt"),
        quality=params.get("q")
    )
