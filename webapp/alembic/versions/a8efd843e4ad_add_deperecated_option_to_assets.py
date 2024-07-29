"""add deperecated option to assets

Revision ID: a8efd843e4ad
Revises: 6652ef3aa77f
Create Date: 2023-04-12 18:08:21.932199

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a8efd843e4ad"
down_revision = "6652ef3aa77f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "asset", sa.Column("deprecated", sa.Boolean(), nullable=True)
    )
    op.execute("UPDATE asset SET deprecated = FALSE")
    op.alter_column("asset", "deprecated", nullable=False)


def downgrade():
    op.drop_column("asset", "deprecated")
