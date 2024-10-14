# System
import imghdr
from base64 import b64decode
from datetime import datetime
from sqlalchemy.dialects import postgresql

# Packages
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.sql.sqltypes import Text
from wand.image import Image
from sqlalchemy import func

# Local
from webapp.database import db_session
from webapp.lib.processors import ImageProcessor
from webapp.lib.url_helpers import clean_unicode
from webapp.lib.file_helpers import is_svg
from webapp.models import Asset, Tag, Product, Author
from webapp.swift import file_manager


class AssetService:

    def find_assets(
        self,
        tag: str,
        asset_type: str,
        product_types: list,
        author_email: str,
        title: str,
        start_date: str,
        end_date: str,
        sf_campg_id: str,
        language: str,
    ):
        """
        Find assets that matches the given criterions
        """
        conditions = []
        if tag:
            conditions.append(Asset.tags.any(Tag.name == tag))
        if asset_type:
            conditions.append(Asset.asset_type == asset_type)
        if author_email:
            conditions.append(Asset.author_email == author_email)
        if title:
            conditions.append(Asset.name.ilike(f"%{title}%"))
        if language:
            conditions.append(Asset.language.ilike(f"{language}"))
        if sf_campg_id:
            conditions.append(
                Asset.salesforce_campaign_id.ilike(f"{sf_campg_id}")
            )
        if end_date and start_date:
            conditions.append(Asset.created.between(start_date, end_date))
        if product_types:
            conditions.append(
                Asset.products.any(Product.name.in_(product_types))
            )

        assets = db_session.query(Asset).filter(*conditions).yield_per(100)
        for asset in assets:
            yield asset

    def find_asset(self, file_path):
        """
        Find an asset that has that matches the exact give file_path or None
        """
        return (
            db_session.query(Asset)
            .filter(Asset.file_path == file_path)
            .one_or_none()
        )

    def create_asset(
        self,
        file_content,
        friendly_name,
        optimize,
        url_path=None,
        tags=[],
        data={},
    ):
        """
        Create a new asset
        """
        # escape unicde characters
        friendly_name = clean_unicode(friendly_name)
        url_path = clean_unicode(url_path)

        encoded_file_content = (b64decode(file_content),)
        if imghdr.what(None, h=file_content) is not None or is_svg(
            file_content
        ):
            data["image"] = True
        else:
            # As it's not an image, there is no need for optimization
            data["optimized"] = False

        # Try to optimize the asset if it's an image
        if data.get("image") and optimize:
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

        if data.get("image"):
            try:
                with Image(blob=encoded_file_content) as image_info:
                    data["width"] = image_info.width
                    data["height"] = image_info.height
            except Exception:
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
        asset = Asset(
            file_path=url_path, data=data, tags=[], created=datetime.utcnow()
        )
        tags = self.create_tags_if_not_exist(tags)
        asset.tags = tags
        db_session.add(asset)
        db_session.commit()
        return asset

    def create_tags_if_not_exist(self, tag_names):
        """
        Create the given tag name if it's new and return the
        object from the database
        """
        tag_names = list(
            set([self.normalize_tag_name(name) for name in tag_names if name])
        )
        existing_tags = (
            db_session.query(Tag).filter(Tag.name.in_(tag_names)).all()
        )
        existing_tag_names = set([tag.name for tag in existing_tags])
        tag_names_to_create = [
            name for name in tag_names if name not in existing_tag_names
        ]

        tags_to_create = []
        for tag_name in tag_names_to_create:
            tag = Tag(name=tag_name, assets=[])
            tags_to_create.append(tag)
        db_session.add_all(tags_to_create)
        db_session.commit()
        return [*existing_tags, *tags_to_create]

    def normalize_tag_name(self, tag_name):
        return tag_name.strip().lower()

    def update_asset(self, file_path, tags=[], deprecated=None):
        asset = (
            db_session.query(Asset)
            .filter(Asset.file_path == file_path)
            .one_or_none()
        )

        if not asset:
            raise AssetNotFound(file_path)
        tags = self.create_tags_if_not_exist(tags)
        asset.tags = tags
        if deprecated is not None:
            asset.deprecated = deprecated
        db_session.commit()
        return asset


class AssetAlreadyExistException(Exception):
    """
    Raised when the requested asset to create already exists
    """

    pass


class AssetNotFound(Exception):
    """
    Raised when the requested asset wasn't found
    """

    pass


asset_service = AssetService()
