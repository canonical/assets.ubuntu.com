from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table

Base = declarative_base()


class Token(Base):
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


class Asset(Base):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)
    file_path = Column(String, nullable=False)
    tags = relationship(
        "Tag", secondary=asset_tag_association_table, back_populates="assets"
    )

    def as_json(self):
        return {
            **self.data,
            "created": self.created.strftime("%a, %d %b %Y %H:%M:%S"),
            "file_path": self.file_path,
            "tags": ", ".join(self.tags),
        }


class Tag(Base):
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


class Redirect(Base):
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
