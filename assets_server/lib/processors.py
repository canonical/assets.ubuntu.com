# System
from io import BytesIO
import os

# Modules
from pilbox.errors import PilboxError
from pilbox.image import Image as PilboxImage
from scour.scour import scourString
from sh import jpegtran, optipng
from uuid import uuid4
from wand.image import Image as WandImage
from xml.parsers.expat import ExpatError
import magic

# Local
from python_helpers import shared_items


class ImageProcessor:
    operation_parameters = {
        'region': ['rect'],
        'rotate': ['deg'],
        'resize': ['w', 'h']
    }

    def __init__(self, image_contents, options={}):
        self.data = image_contents
        self.options = options

    def process(self):
        """
        Reformat, optimize or transform an image
        """

        target_format = self.options.get('fmt')
        optimize = self.options.get("opt") is not None

        # Reformat images
        converted = self.convert(target_format)

        # Do transformations
        transformed = self.transform()

        # Optimize images
        if converted or transformed or optimize:
            self.optimize(allow_svg_errors=converted or transformed)

    def optimize(self, allow_svg_errors=False):
        """
        Optimize SVGs, PNGs or Jpegs
        Unfortunately, this needs to write temporary files
        by making use of the /tmp directory
        """

        mimetype = magic.Magic(mime=True).from_buffer(self.data)
        tmp_filename = '/tmp/' + uuid4().get_hex()

        if mimetype == 'image/svg+xml':
            try:
                self.data = str(scourString(self.data))
            except ExpatError as optimize_error:
                if optimize_error.code == 27 and allow_svg_errors:
                    # Invalid SVG. Let's just not optimize it
                    pass
                else:
                    raise optimize_error
            except UnicodeEncodeError:
                # SVG contains binary data, we can't optimise it
                pass

        elif mimetype == 'image/jpeg':
            self.data = jpegtran("-optimize", _in=self.data).stdout

        elif mimetype == 'image/png':
            with open(tmp_filename, 'w') as tmp:
                tmp.write(self.data)
            optipng(tmp_filename)
            with open(tmp_filename) as tmp:
                self.data = tmp.read()
            os.remove(tmp_filename)

    def convert(self, target_format):
        if not target_format:
            return False
        if target_format in ['png', 'jpg', 'gif']:
            # Do conversion with wand
            with WandImage(blob=self.data) as image:
                self.data = image.make_blob(target_format)
                return True
        else:
            raise PilboxError(
                400,
                log_message="Cannot convert to '{}'".format(target_format)
            )

    def transform(self):
        """
        Perform transformations on an image
        Using Pilbox: https://github.com/nottrobin/pilbox
        The self.options follow Pilbox's API

        Return True if transformation happened
        """

        # Operations (region, rotate, resize...)
        # ---

        mimetype = magic.Magic(mime=True).from_buffer(self.data)

        if mimetype in ['image/png', 'image/jpeg', 'image/gif']:
            operation = self.options.get('op')

            if (
                not operation and
                shared_items(self.options, self.operation_parameters['resize'])
            ):
                operation = "resize"

            if operation or 'q' in self.options:
                try:
                    self._pilbox_operation(operation)
                except (TypeError, AttributeError) as operation_error:
                    self._missing_param_error(operation_error, operation)

                return True

    # Private helper methods
    # ===

    def _pilbox_operation(self, operation):
        """
        Use Pilbox to transform an image
        """

        image = PilboxImage(BytesIO(self.data))

        if operation == "region":
            image.region(
                self.options.get("rect").split(',')
            )

        elif operation == "rotate":
            image.rotate(
                deg=self.options.get("deg"),
                expand=self.options.get("expand")
            )
        elif operation == "resize":
            resize_width = self.options.get("w")
            resize_height = self.options.get("h")

            # Make sure widths and heights are integers
            if resize_width:
                resize_width = int(resize_width)
            if resize_height:
                resize_height = int(resize_height)

            if resize_width or resize_height:
                # Don't allow expanding of images
                with WandImage(blob=self.data) as image_info:
                    if (
                        resize_width > image_info.width or
                        resize_height > image_info.height
                    ):
                        expand_message = (
                            "Resize error: Maximum dimensions for this image "
                            "are {0}px wide by {1}px high."
                        ).format(image_info.width, image_info.height)

                        raise PilboxError(
                            400,
                            log_message=expand_message
                        )

            image.resize(
                width=resize_width,
                height=resize_height,
                mode=self.options.get("mode"),
                filter=self.options.get("filter"),
                background=self.options.get("bg"),
                retain=self.options.get("retain"),
                position=self.options.get("pos")
            )

        self.data = image.save(quality=self.options.get("q")).read()

    def _missing_param_error(self, error, operation):
        expected_errors = [
            "int() argument must be a string or a number, not 'NoneType'",
            "'NoneType' object has no attribute 'split'"
        ]

        if error.message in expected_errors:
            message = (
                "Invalid image operation. '{0}' accepts: {1}. "
                "See https://github.com/agschwender/pilbox for more detail."
            ).format(
                operation,
                ', '.join(self.operation_parameters[operation])
            )

            raise PilboxError(400, log_message=message)
        else:
            raise error
