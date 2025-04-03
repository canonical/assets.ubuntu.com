"""squash_assets_improvements

Revision ID: 14e1e1dfca79
Revises: 62f9c9a26cce
Create Date: 2025-04-03 13:42:24.559843

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "14e1e1dfca79"
down_revision = "62f9c9a26cce"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "author",
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("first_name", "last_name", "email"),
        sa.UniqueConstraint("email"),
    )
    op.add_column("asset", sa.Column("author_email", sa.String(), nullable=True))
    op.add_column("asset", sa.Column("file_type", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_asset_author", "asset", "author", ["author_email"], ["email"]
    )


def downgrade():
    op.drop_constraint("fk_asset_author", "asset", type_="foreignkey")
    op.drop_column("asset", "file_type")
    op.drop_column("asset", "author_email")
    op.drop_table("author")
