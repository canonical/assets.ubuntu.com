from dataclasses import dataclass


@dataclass
class AssetSearchParams:
    tag: str = ""
    asset_type: str = ""
    product_types: list = None
    author_email: str = ""
    name: str = ""
    start_date: str = None
    end_date: str = None
    language: str = ""
    file_types: list = None

    def __post_init__(self):
        if self.product_types is None:
            self.product_types = []
        if self.file_types is None:
            self.file_types = []
        for product in self.product_types[:]:
            product = product.strip()
            if not product:
                self.product_types.remove(product)
        for file_type in self.file_types[:]:
            file_type = file_type.strip()
            if not file_type:
                self.file_types.remove(file_type)
