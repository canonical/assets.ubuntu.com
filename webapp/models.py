from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table

Base = declarative_base()


class DateTimeMixin(Base):
    __abstract__ = True
    created = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    updated = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )


class Token(DateTimeMixin):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    token = Column(String, nullable=False)


asset_tag_association_table = Table(
    "asset_tag_association",
    Base.metadata,
    Column("asset_id", ForeignKey("asset.id"), primary_key=True),
    Column("tag_name", ForeignKey("tag.name"), primary_key=True),
)

asset_campaign_association_table = Table(
    "asset_campaign_association",
    Base.metadata,
    Column("asset_id", ForeignKey("asset.id"), primary_key=True),
    Column(
        "campaign_id", ForeignKey("salesforce_campaign.id"), primary_key=True
    ),
)

asset_product_association_table = Table(
    "asset_product_association",
    Base.metadata,
    Column("asset_id", ForeignKey("asset.id"), primary_key=True),
    Column("product_name", ForeignKey("product.name"), primary_key=True),
)

asset_category_association_table = Table(
    "asset_category_association",
    Base.metadata,
    Column("asset_id", ForeignKey("asset.id"), primary_key=True),
    Column("category_name", ForeignKey("category.name"), primary_key=True),
)


class Author(Base):
    __tablename__ = "author"

    first_name = Column(String, nullable=False, primary_key=True)
    last_name = Column(String, nullable=False, primary_key=True)
    email = Column(String, nullable=False, unique=True, primary_key=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Asset(DateTimeMixin):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True)
    asset_type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    google_drive_link = Column(String, nullable=True)
    language = Column(String, nullable=True)
    data = Column(JSON, nullable=False)
    file_path = Column(String, nullable=False)
    author_email = Column(String, ForeignKey("author.email"), nullable=True)
    author = relationship("Author")
    tags = relationship(
        "Tag", secondary=asset_tag_association_table, back_populates="assets"
    )
    products = relationship(
        "Product",
        secondary=asset_product_association_table,
        back_populates="assets",
    )
    salesforce_campaigns = relationship(
        "Salesforce_Campaign",
        secondary=asset_campaign_association_table,
        back_populates="assets",
    )
    categories = relationship(
        "Category",
        secondary=asset_category_association_table,
        back_populates="assets",
    )
    file_type = Column(String, nullable=True)
    deprecated = Column(Boolean, nullable=False, default=False)

    def as_json(self):
        return {
            **self.data,
            "created": self.created.strftime("%a, %d %b %Y %H:%M:%S"),
            "file_path": self.file_path,
            "tags": ", ".join([tag.name for tag in self.tags]),
            "products": ", ".join([product.name for product in self.products]),
            "categories": ", ".join(
                [category.name for category in self.categories]
            ),
            "deprecated": self.deprecated,
            "asset_type": self.asset_type,
            "name": self.name,
            "author": (
                {
                    "first_name": (
                        self.author.first_name if self.author else None
                    ),
                    "last_name": (
                        self.author.last_name if self.author else None
                    ),
                    "email": self.author.email if self.author else None,
                }
                if self.author
                else None
            ),
            "google_drive_link": self.google_drive_link,
            "salesforce_campaigns": [
                campaign.as_json() for campaign in self.salesforce_campaigns
            ],
            "language": self.language,
            "file_type": self.file_type,
        }


class Tag(DateTimeMixin):
    __tablename__ = "tag"
    name = Column(String, primary_key=True)
    assets = relationship(
        "Asset", secondary=asset_tag_association_table, back_populates="tags"
    )

    def as_json(self):
        return {
            "name": self.name,
            "assets": ", ".join(self.assets),
        }


class Salesforce_Campaign(DateTimeMixin):
    __tablename__ = "salesforce_campaign"
    name = Column(String, nullable=True)
    id = Column(String, primary_key=True)
    assets = relationship(
        "Asset",
        secondary=asset_campaign_association_table,
        back_populates="salesforce_campaigns",
    )

    def as_json(self):
        return {
            "name": self.name,
            "id": self.id,
        }


class Product(DateTimeMixin):
    __tablename__ = "product"
    name = Column(String, primary_key=True)
    assets = relationship(
        "Asset",
        secondary=asset_product_association_table,
        back_populates="products",
    )

    def as_json(self):
        return {
            "name": self.name,
            "assets": ", ".join(self.assets),
        }


class Category(DateTimeMixin):
    __tablename__ = "category"
    name = Column(String, primary_key=True)
    assets = relationship(
        "Asset",
        secondary=asset_category_association_table,
        back_populates="categories",
    )

    def as_json(self):
        return {
            "name": self.name,
            "assets": ", ".join(self.assets),
        }


class Redirect(DateTimeMixin):
    __tablename__ = "redirect"

    id = Column(Integer, primary_key=True)
    redirect_path = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    permanent = Column(Boolean, nullable=False)

    def as_json(self):
        return {
            "redirect_path": self.redirect_path,
            "target_url": self.target_url,
            "permanent": self.permanent,
        }
