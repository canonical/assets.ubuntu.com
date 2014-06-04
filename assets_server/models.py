class Asset:
    def __init__(self, filename, tags, created, png_filename=''):
        self.filename = filename
        self.tags = tags
        self.created = created
        self.png_filename = png_filename
