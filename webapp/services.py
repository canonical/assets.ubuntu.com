# System
import imghdr
from base64 import b64decode
from datetime import datetime
from typing import Tuple

# Packages
from sqlalchemy import func
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.sql.sqltypes import Text
from wand.image import Image
from sqlalchemy import func
# Local
from webapp.database import db_session
from webapp.lib.file_helpers import is_svg
from webapp.lib.processors import ImageProcessor
from webapp.lib.url_helpers import clean_unicode
from webapp.models import Asset, Tag
from webapp.lib.file_helpers import is_svg
from webapp.models import Asset, Tag , Product, Author
from webapp.swift import file_manager
from webapp.utils import lru_cache


class AssetService:
    def find_assets(
        self,
        file_type="%",
        tag="abc",
        asset_type = "png",
        product_types=["a","b"],
        author_email="abc@g.com",
        title="mad",
        start_date="2024-01-01",
        end_date="2024-10-14",
        sf_campg_id="1234",
        language="en",
        query=None,
        page=1,
        per_page=10,
        order_by=Asset.created,
        desc_order=True,
        include_deprecated=False,
    ) -> Tuple[list, int]:
        """
        Find assets that matches the given criterions
        """
        tag = "gif"
        if not tag:
            tag = "%"
        if not asset_type:
            asset_type = "%"
        if not author_email:
            author_email = "%"
        if not title:
            title = "%"
        if not language:
            language = "%"
        if not sf_campg_id:
            sf_campg_id = "%"
    
        conditions = [
            Asset.tags.any(Tag.name == tag),
            Asset.asset_type == asset_type,
            Asset.name.ilike(f"%{title}%"),
            Asset.language == language,
            Asset.salesforce_campaign_id == sf_campg_id,
            Asset.author_email == author_email
        ]
        if tag:
            tag_condition = Asset.tags.any(Tag.name == tag)
            conditions.append(tag_condition)

        if not include_deprecated:
            conditions.append(Asset.deprecated.is_(False))

        if order_by == Asset.file_path:
            # Example: "86293d6f-FortyCloud.png" -> "FortyCloud.png"
            order_col = func.split_part(Asset.file_path, "-", 2)
        else:
            order_col = order_by

        if (end_date and start_date):
            conditions.append(Asset.created.between(start_date, end_date))

        if product_types:
                conditions.append(Asset.products.any(Product.name.in_(product_types)))

        assets_query = (
            db_session.query(Asset)
            .filter(*conditions)
            .order_by(order_col.desc() if desc_order else order_col)
            .offset((page - 1) * per_page)
            .yield_per(100)
        )

        assets = assets_query.limit(per_page).all()

        total = db_session.query(Asset).filter(*conditions).count()
        return assets, total

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

    @lru_cache(ttl_seconds=3600)
    def available_extensions(self):
        """
        Return a list of available extensions
        """
        # get distinct file_path only the 7 last characters
        files = (
            db_session.query(Asset.file_path).distinct(Asset.file_path).all()
        )
        extensions = set()
        for file in files:
            file_path = file[0]
            extension = file_path.split(".")[-1].lower()
            if len(extension) < 7 and len(extension) > 2:
                extensions.add(extension)
        return extensions

    @staticmethod
    def order_by_fields():
        """
        Fields that can be used to order assets by.
        """
        return {
            "Creation date": Asset.created,
            "File name": Asset.file_path,
        }


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
