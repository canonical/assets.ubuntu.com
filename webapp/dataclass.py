from dataclasses import dataclass, field


@dataclass
class AssetSearchParams:
    tag: str = ""
    asset_type: str = ""
    product_types: list = field(default_factory=list)
    author_email: str = ""
    name: str = ""
    start_date: str = None
    end_date: str = None
    language: str = ""
    file_types: list = field(default_factory=list)
    categories: list = field(default_factory=list)

    def __post_init__(self):
        for product in self.product_types[:]:
            product = product.strip()
            if not product:
                self.product_types.remove(product)
        for category in self.categories[:]:
            category = category.strip()
            if not category:
                self.categories.remove(category)
        for file_type in self.file_types[:]:
            file_type = file_type.strip()
            if not file_type:
                self.file_types.remove(file_type)
