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
    salesforce_campaign_id: str = ""
    language: str = ""

    def __post_init__(self):
        if self.product_types is None:
            self.product_types = []
        for product in self.product_types[:]:
            product = product.strip()
            if not product:
                self.product_types.remove(product)