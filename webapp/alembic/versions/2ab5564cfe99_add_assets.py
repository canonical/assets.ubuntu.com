"""add_assets

Revision ID: 2ab5564cfe99
Revises: eb9f8639d610
Create Date: 2020-01-09 14:37:08.316607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ab5564cfe99"
down_revision = "eb9f8639d610"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "asset",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("asset")
