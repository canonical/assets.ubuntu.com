# System
from base64 import b64decode
from datetime import datetime
import imghdr

# Packages
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.sqltypes import Text
from wand.image import Image

# Local
from webapp.database import db_session
from webapp.lib.processors import ImageProcessor
from webapp.models import Asset
from webapp.swift import file_manager


class AssetService:
    def find_assets(self, file_type="", query=None):
        """
        Find assets that matches the given criterions
        """
        if not query:
            return db_session.query(Asset).all()

        return (
            db_session.query(Asset)
            .filter(
                Asset.file_path.endswith(f".{file_type}%"),
                or_(
                    Asset.file_path.ilike(f"%{query}%"),
                    Asset.data.cast(Text).ilike(f"%{query}%"),
                ),
            )
            .all()
        )

    def create_asset(
        self, file_content, friendly_name, optimize, url_path=None, data={}
    ):
        """
        Create a new asset
        """
        encoded_file_content = (b64decode(file_content),)
        if imghdr.what(None, h=file_content) is not None:
            data["image"] = True
        else:
            # As it's not an image, there is no need for optimization
            data["optimized"] = False
        # Try to optimize the asset if it's an image
        if data["image"] and optimize:
            try:
                image = ImageProcessor(encoded_file_content)
                image.optimize(allow_svg_errors=True)
                encoded_file_content = image.data
                data["optimized"] = True
            except Exception:
                # If optimisation failed, just don't bother optimising
                data["optimized"] = False
        if not url_path:
            url_path = file_manager.generate_asset_path(
                file_content, friendly_name
            )

        if data["image"]:
            try:
                with Image(blob=encoded_file_content) as image_info:
                    data["width"] = image_info.width
                    data["height"] = image_info.height
            except Exception as e:
                print("e", e)
                # Just don't worry if image reading fails
                pass

        asset = (
            db_session.query(Asset)
            .filter(Asset.file_path == url_path)
            .one_or_none()
        )

        if asset:
            if "width" not in asset.data and "width" in data:
                asset.data["width"] = data["width"]

            if "height" not in asset.data and "height" in data:
                asset.data["height"] = data["height"]

            db_session.commit()

            raise AssetAlreadyExistException(url_path)

        # Save the file in Swift
        file_manager.create(file_content, url_path)

        # Save file info in Postgres
        asset = Asset(file_path=url_path, data=data, created=datetime.utcnow())
        db_session.add(asset)
        db_session.commit()

        return asset


class AssetAlreadyExistException(Exception):
    """
    Raised when the requested asset to create already exists
    """

    pass


asset_service = AssetService()
