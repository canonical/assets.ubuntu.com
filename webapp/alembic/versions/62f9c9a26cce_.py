"""empty message

Revision ID: 62f9c9a26cce
Revises: a8efd843e4ad
Create Date: 2024-09-24 12:56:52.278399

"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "62f9c9a26cce"
down_revision = "a8efd843e4ad"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "product",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
        sa.Column(
            "updated", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "asset_product_association",
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["asset.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_name"],
            ["product.name"],
        ),
        sa.PrimaryKeyConstraint("asset_id", "product_name"),
    )
    op.add_column("asset", sa.Column("asset_type", sa.String(), nullable=True))
    op.add_column("asset", sa.Column("name", sa.String(), nullable=True))
    op.add_column("asset", sa.Column("author", sa.String(), nullable=True))
    op.add_column(
        "asset", sa.Column("google_drive_link", sa.String(), nullable=True)
    )
    op.add_column(
        "asset",
        sa.Column("salesforce_campaign_id", sa.String(), nullable=True),
    )
    op.add_column("asset", sa.Column("language", sa.String(), nullable=True))
    op.add_column(
        "asset",
        sa.Column(
            "updated", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )
    op.add_column(
        "redirect",
        sa.Column(
            "created", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )
    op.add_column(
        "redirect",
        sa.Column(
            "updated", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )
    op.add_column(
        "tag",
        sa.Column(
            "created", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )
    op.add_column(
        "tag",
        sa.Column(
            "updated", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )
    op.add_column(
        "token",
        sa.Column(
            "created", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )
    op.add_column(
        "token",
        sa.Column(
            "updated", sa.DateTime(), nullable=False, server_default=str(datetime.now())
        ),
    )


def downgrade():
    op.drop_column("token", "updated")
    op.drop_column("token", "created")
    op.drop_column("tag", "updated")
    op.drop_column("tag", "created")
    op.drop_column("redirect", "updated")
    op.drop_column("redirect", "created")
    op.drop_column("asset", "updated")
    op.drop_column("asset", "language")
    op.drop_column("asset", "salesforce_campaign_id")
    op.drop_column("asset", "google_drive_link")
    op.drop_column("asset", "author")
    op.drop_column("asset", "name")
    op.drop_column("asset", "asset_type")
    op.drop_table("asset_product_association")
    op.drop_table("product")
