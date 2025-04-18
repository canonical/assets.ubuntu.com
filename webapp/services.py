# System
import imghdr
from base64 import b64decode, b64encode
from datetime import datetime, timezone
from io import BytesIO
from typing import List, Tuple

from PIL import Image as PillowImage

# Packages
from sqlalchemy import func, or_

# Local
from webapp.database import db_session
from webapp.lib.file_helpers import is_svg
from webapp.lib.processors import ImageProcessor
from webapp.lib.url_helpers import clean_unicode
from webapp.models import Asset, Author, Product, Tag
from webapp.swift import file_manager
from webapp.utils import lru_cache


class AssetService:
    def find_all_assets(self):
        """
        Return all assets in the database as a list
        """
        assets = db_session.query(Asset).all()
        return assets

    def find_assets(
        self,
        tag: str = "abc",
        asset_type: str = "image",
        product_types: list = ["a", "b"],
        author_email: str = "abc@g.com",
        start_date: str = "2024-01-01",
        end_date: str = "2024-10-14",
        salesforce_campaign_id: str = "1234",
        language: str = "English",
        page=1,
        per_page=6,
        order_by=Asset.created,
        desc_order=True,
        include_deprecated=False,
        file_types: list = ["a", "b"],
    ) -> Tuple[list, int]:
        """
        Find assets that matches the given criterions
        """
        conditions = []
        if tag:
            conditions.append(
                or_(
                    Asset.tags.any(Tag.name == tag),
                    Asset.products.any(Product.name == tag),
                    Asset.name.ilike(f"%{tag}%"),
                    Asset.file_path.ilike(f"%{tag}%"),
                ),
            )
        if asset_type:
            conditions.append(Asset.asset_type == asset_type)
        if author_email:
            conditions.append(Asset.author_email == author_email)
        if language:
            conditions.append(Asset.language.ilike(f"{language}"))
        if salesforce_campaign_id:
            conditions.append(
                Asset.salesforce_campaign_id.ilike(
                    f"{salesforce_campaign_id}",
                ),
            )

        if not include_deprecated:
            conditions.append(Asset.deprecated.is_(False))

        if order_by == Asset.file_path:
            # Example: "86293d6f-FortyCloud.png" -> "FortyCloud.png"
            order_col = func.split_part(Asset.file_path, "-", 2)
        else:
            order_col = order_by

        if end_date and start_date:
            conditions.append(Asset.created.between(start_date, end_date))
        if product_types:
            conditions.append(
                Asset.products.any(Product.name.in_(product_types)),
            )

        if file_types:
            conditions.append(Asset.file_type.in_(file_types))

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
        friendly_name: str,
        optimize: bool,
        name: str = None,
        url_path: str = None,
        tags: List[str] = [],
        products: List[str] = [],
        asset_type: str = "image",
        author: dict = None,
        google_drive_link: str = None,
        salesforce_campaign_id: str = None,
        language: str = "English",
        deprecated: bool = False,
        data={},
    ):
        """
        Create a new asset
        """
        # escape unicde characters
        friendly_name = clean_unicode(friendly_name)
        url_path = clean_unicode(url_path)

        # First we ensure it is b64 encoded
        encoded_file_content = b64encode(file_content)
        # Then we can decode it
        decoded_file_content = b64decode(encoded_file_content)

        if imghdr.what(None, h=file_content) is not None or is_svg(
            file_content,
        ):
            data["image"] = True
        else:
            # As it's not an image, there is no need for optimization
            data["optimized"] = False
        if data.get("image"):
            try:
                # Use Pillow to open the image and get dimensions
                with PillowImage.open(BytesIO(decoded_file_content)) as img:
                    data["width"] = img.width
                    data["height"] = img.height
            except Exception as e:
                print(f"Error opening image with Pillow: {e}")
                data["width"] = None
                data["height"] = None

        # Try to optimize the asset if it's an image
        if data.get("image") and optimize:
            try:
                image = ImageProcessor(decoded_file_content)
                image.optimize(allow_svg_errors=True)
                decoded_file_content = image.data
                data["optimized"] = True
            except Exception:
                # If optimisation failed, just don't bother optimising
                data["optimized"] = False

        if not url_path:
            url_path = file_manager.generate_asset_path(
                file_content,
                friendly_name,
            )

        try:
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
            tags = self.create_tags_if_not_exist(tags)
            products = self.create_products_if_not_exists(products)
            _author = self.create_author_if_not_exist(author)

            # Save file info in Postgres
            asset = Asset(
                file_path=url_path,
                name=name,
                data=data,
                tags=tags,
                created=datetime.now(tz=timezone.utc),
                products=products,
                asset_type=asset_type,
                author=_author,
                google_drive_link=google_drive_link,
                salesforce_campaign_id=salesforce_campaign_id,
                language=language,
                deprecated=deprecated,
                file_type=url_path.split(".")[-1].lower(),
            )
            db_session.add(asset)
            db_session.commit()

        # Rollback transaction if any error occurs
        except Exception:
            db_session.rollback()
            raise
        else:
            return asset

    def create_tags_if_not_exist(self, tag_names):
        """
        Create the given tag name if it's new and return the
        object from the database
        """
        tag_names = list(
            set([self.normalize_tag_name(name) for name in tag_names if name]),
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

    def create_products_if_not_exists(self, product_names):
        """
        Create the product objects and return the
        object from the database
        """
        if product_names == [""]:
            return []

        product_objects = []
        for product_name in product_names:
            existing_product = (
                db_session.query(Product).filter_by(name=product_name).first()
            )

            if existing_product:
                product_objects.append(existing_product)
            else:
                product = Product(name=product_name, assets=[])
                product_objects.append(product)
                db_session.add(product)

        db_session.commit()
        return product_objects

    def create_author_if_not_exist(
        self,
        author,
    ):
        """
        Create the author object and return the object from the database
        """
        if not (email := author.get("email")):
            return None

        possible_names = email.split("@")[0].split(".")
        # If not supplied, we use the email to get the first name
        # The reason we want to derive this from the email is that most emails
        # follow a predictable fname.lname@host format, and not all authors
        # might be on launchpad (especially for cli tools).
        if not (first_name := author.get("first_name")):
            first_name = possible_names[0]

        # If we don't have a last name
        if not (last_name := author.get("last_name")):
            try:
                # use name from email
                last_name = possible_names[1]
            except IndexError:
                # or a reversed first_name
                last_name = first_name[::-1]

        existing_author = (
            db_session.query(Author).filter_by(email=email).first()
        )

        if existing_author:
            return existing_author

        author_data = Author(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        db_session.add(author_data)
        db_session.commit()
        return db_session.query(Author).filter_by(email=email).first()

    def normalize_tag_name(self, tag_name):
        return tag_name.strip().lower()

    def update_asset(
        self,
        file_path: str,
        name: str = None,
        tags: List[str] = [],
        deprecated: bool = None,
        products: List[str] = [],
        asset_type: str = "image",
        author: str = None,
        google_drive_link: str = None,
        salesforce_campaign_id: str = None,
        language: str = "English",
    ):
        asset = (
            db_session.query(Asset)
            .filter(Asset.file_path == file_path)
            .one_or_none()
        )
        if not asset:
            raise AssetNotFound(file_path)

        if tags:
            tags = self.create_tags_if_not_exist(tags)
            asset.tags = tags
        if name:
            asset.name = name
        if products:
            products = self.create_products_if_not_exists(products)
            asset.products = products
        if asset_type:
            asset.asset_type = asset_type
        if author:
            asset.author = self.create_author_if_not_exist(author)
        if google_drive_link:
            asset.google_drive_link = google_drive_link
        if salesforce_campaign_id:
            asset.salesforce_campaign_id = salesforce_campaign_id
        if language:
            asset.language = language
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


class AssetNotFound(Exception):
    """
    Raised when the requested asset wasn't found
    """


asset_service = AssetService()
