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
        title=request.args.get("title", "").strip(),
        start_date=request.args.get("start_date", None),
        end_date=request.args.get("end_date", None),
        sf_campg_id=request.args.get("sf_campg_id", "").strip(),
        language=request.args.get("language", "").strip(),
    )