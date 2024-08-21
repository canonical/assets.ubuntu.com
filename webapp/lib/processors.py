import os
from io import BytesIO
from uuid import uuid4

from more_itertools import unique_everseen
from PIL import Image as PILImage
from scour.scour import scourString
from sh import jpegtran, optipng
from wand.image import Image as WandImage

from webapp.lib.file_helpers import guess_mime
from webapp.lib.python_helpers import shared_items


class ImageProcessingError(Exception):
    def __init__(self, status_code, log_message):
        self.status_code = status_code
        self.log_message = log_message
        super().__init__(log_message)


class ImageProcessor:
    operation_parameters = {
        "region": ["rect"],
        "rotate": ["deg"],
        "resize": ["w", "h", "max-width", "max-height"],
    }

    def __init__(self, image_contents, options={}):
        self.data = image_contents
        self.options = options

    def process(self):
        """
        Reformat, optimize or transform an image
        """

        target_format = self.options.get("fmt")
        optimize = self.options.get("opt") is not None

        # Reformat images
        converted = self.convert(target_format)

        # Do transformations
        transformed = self.transform()

        # Optimize images
        if converted or transformed or optimize:
            self.optimize(allow_svg_errors=converted or transformed)

        return target_format

    def optimize(self, allow_svg_errors=False):
        """
        Optimize SVGs, PNGs or Jpegs
        Unfortunately, this needs to write temporary files
        by making use of the /tmp directory
        """

        mimetype = guess_mime(self.data)
        tmp_filename = "/tmp/" + uuid4().hex

        if mimetype == "image/svg+xml":
            try:
                self.data = str(scourString(self.data))
            except Exception:
                # SVG contains bad data, we can't optimise it
                pass

        elif mimetype == "image/jpeg":
            self.data = jpegtran("-optimize", _in=self.data).stdout

        elif mimetype == "image/png":
            with open(tmp_filename, "wb") as tmp:
                tmp.write(self.data)
            optipng(tmp_filename)
            with open(tmp_filename, "rb") as tmp:
                self.data = tmp.read()
            os.remove(tmp_filename)

    def convert(self, target_format):
        if not target_format:
            return False
        if target_format in ["png", "jpg", "gif"]:
            # Do conversion with wand
            with WandImage(blob=self.data) as image:
                self.data = image.make_blob(target_format)
                return True
        else:
            raise ImageProcessingError(
                400, log_message="Cannot convert to '{}'".format(target_format)
            )

    def transform(self):
        """
        Perform transformations on an image
        Using Pillow
        The self.options follow the provided API

        Return True if transformation happened
        """

        # Operations (region, rotate, resize...)
        # ---
        mimetype = guess_mime(self.data)

        if mimetype in ["image/png", "image/jpeg", "image/gif"]:
            operation = self.options.get("op")

            if not operation and shared_items(
                self.options, self.operation_parameters["resize"]
            ):
                operation = "resize"

            operations = operation.split(",") if operation else []
            # Remove duplicate operations from list
            operations = unique_everseen(operations)

            for operation in operations:
                if operation or "q" in self.options:
                    try:
                        self._pillow_operation(operation)
                    except (
                        IndexError,
                        ValueError,
                        TypeError,
                        AttributeError,
                    ):
                        self._missing_param_error(operation)

            if operation:
                return True

    # Private helper methods
    # ===

    def _pillow_operation(self, operation):
        """
        Use Pillow to transform an image
        """

        image = PILImage.open(BytesIO(self.data))

        if operation == "region":
            rect = tuple(map(int, self.options.get("rect").split(",")))
            image = image.crop(rect)

        elif operation == "rotate":
            deg = -1 * int(self.options.get("deg"))
            expand = self.options.get("expand")
            image = image.rotate(deg, expand=expand)
        elif operation == "resize":
            max_width = self.options.get("max-width")
            max_height = self.options.get("max-height")

            resize_width = self.options.get("w")
            resize_height = self.options.get("h")

            # Make sure widths and heights are integers
            if resize_width:
                resize_width = int(resize_width)
            if resize_height:
                resize_height = int(resize_height)
            if max_width:
                max_width = int(max_width)
            if max_height:
                max_height = int(max_height)

            # Image size management
            image_width, image_height = image.size

            # Don't allow expanding of images
            if (resize_width and resize_width > image_width) or (
                resize_height and resize_height > image_height
            ):
                expand_message = (
                    "Resize error: Maximum dimensions for this image "
                    "are {0}px wide by {1}px high."
                ).format(image_width, image_height)

                raise ImageProcessingError(400, log_message=expand_message)

            # Process max_width and max_height
            if not resize_width and max_width:
                if max_width < image_width:
                    resize_width = max_width

            if not resize_height and max_height:
                if max_height < image_height:
                    resize_height = max_height

            # Conserve the image ratio
            if resize_height and not resize_width:
                image_ratio = image_height / resize_height
                resize_width = int(image_width / image_ratio)
            elif not resize_height and resize_width:
                image_ratio = image_width / resize_width
                resize_height = int(image_height / image_ratio)

            if resize_height or resize_width:
                image = image.resize((resize_width, resize_height))

        image_format = image.format or "PNG"
        with BytesIO() as output:
            image.save(
                output, format=image_format, quality=self.options.get("q")
            )
            self.data = output.getvalue()

    def _missing_param_error(self, operation):
        message = (
            "Invalid image operation. '{0}' accepts: {1}. "
            "See https://github.com/agschwender/pilbox for more detail."
        ).format(operation, ", ".join(self.operation_parameters[operation]))

        raise ImageProcessingError(400, log_message=message)
