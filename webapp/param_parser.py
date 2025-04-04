from flask import request
from webapp.dataclass import AssetSearchParams


def parse_asset_search_params() -> AssetSearchParams:
    """
    Parse request arguments and return AssetSearchParams object with defaults.
    """
    return AssetSearchParams(
        tag=request.args.get("tag", "").strip(),
        asset_type=request.args.get("asset_type", "").strip(),
        product_types=request.args.getlist("product_types") or [],
        author_email=request.args.get("author_email", "").strip(),
        name=request.args.get("name", "").strip(),
        start_date=request.args.get("start_date", None),
        end_date=request.args.get("end_date", None),
        salesforce_campaign_id=request.args.get(
            "salesforce_campaign_id", ""
        ).strip(),
        language=request.args.get("language", "").strip(),
        file_types=request.args.getlist("file_types") or [],
    )
