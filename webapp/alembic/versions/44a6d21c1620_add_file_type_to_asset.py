"""add file type to asset

Revision ID: 44a6d21c1620
Revises: aaf824b40866
Create Date: 2025-02-27 12:37:13.350485

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "44a6d21c1620"
down_revision = "aaf824b40866"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("asset", sa.Column("file_type", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("asset", "file_type")
    # ### end Alembic commands ###
