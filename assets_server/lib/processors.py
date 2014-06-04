from pilbox.image import Image


def image_processor(image_stream, params):
    """
    Perform transformations on an image
    Using Pilbox: https://github.com/nottrobin/pilbox
    The params follow Pilbox's API
    """

    image = Image(image_stream)

    op = params.get("op", "resize")

    if op == "resize":
        image.resize(
            width=params.get("w"),
            height=params.get("h"),
            mode=params.get("mode"),
            filter=params.get("filter"),
            background=params.get("bg"),
            position=params.get("pos")
        )

    elif op == "region":
        image.region(
            params.get("rect").split(',')
        )

    elif op == "rotate":
        image.rotate(
            deg=params.get("deg"),
            expand=params.get("expand")
        )

    return image.save(
        format=params.get("fmt"),
        quality=params.get("q")
    )
