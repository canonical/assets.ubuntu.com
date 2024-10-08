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

asset_product_association_table = Table(
    "asset_product_association",
    Base.metadata,
    Column("asset_id", ForeignKey("asset.id"), primary_key=True),
    Column("product_name", ForeignKey("product.name"), primary_key=True),
)


class Asset(DateTimeMixin):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True)
    asset_type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    author = Column(String, nullable=True)
    google_drive_link = Column(String, nullable=True)
    salesforce_campaign_id = Column(String, nullable=True)
    language = Column(String, nullable=True)
    data = Column(JSON, nullable=False)
    file_path = Column(String, nullable=False)
    tags = relationship(
        "Tag", secondary=asset_tag_association_table, back_populates="assets"
    )
    products = relationship(
        "Product",
        secondary=asset_product_association_table,
        back_populates="assets",
    )
    deprecated = Column(Boolean, nullable=False, default=False)

    def as_json(self):
        return {
            **self.data,
            "created": self.created.strftime("%a, %d %b %Y %H:%M:%S"),
            "file_path": self.file_path,
            "tags": ", ".join([tag.name for tag in self.tags]),
            "deprecated": self.deprecated,
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
