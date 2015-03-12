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
        raise resize_error

def image_processor(image_stream, params):
    """
    Perform transformations on an image
    Using Pilbox: https://github.com/nottrobin/pilbox
    The params follow Pilbox's API
    """

    image = Image(image_stream)

    op = params.get("op")

    resize_operations = ['w', 'h', 'mode', 'filter', 'bg', 'pos']
    used_operations = [x for x in params.keys() if x in resize_operations]

    if op == "region":
        try:
            image.region(
                params.get("rect").split(',')
            )
        except AttributeError as region_error:
            catch_missing_param_error(region_error, 'rotate', ['rect'])

    elif op == "rotate":
        try:
            image.rotate(
                deg=params.get("deg"),
                expand=params.get("expand")
            )
        except TypeError as rotate_error:
            catch_missing_param_error(rotate_error, 'rotate', ['deg', 'expand'])


    elif op == "resize" or used_operations:
        try:
            image.resize(
                width=params.get("w"),
                height=params.get("h"),
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
