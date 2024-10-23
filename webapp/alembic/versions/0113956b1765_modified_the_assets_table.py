"""modified the assets table

Revision ID: 0113956b1765
Revises: 3328567a4fd1
Create Date: 2024-10-08 16:04:59.572741

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0113956b1765"
down_revision = "3328567a4fd1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("asset", "author")
    op.drop_constraint("author_asset_fkey", "author", type_="foreignkey")
    op.drop_column("author", "asset")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "author",
        sa.Column("asset", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "author_asset_fkey", "author", "asset", ["asset"], ["id"]
    )
    op.add_column(
        "asset",
        sa.Column("author", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###