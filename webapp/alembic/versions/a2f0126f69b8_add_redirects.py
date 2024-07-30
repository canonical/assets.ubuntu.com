"""add redirects

Revision ID: a2f0126f69b8
Revises: 2ab5564cfe99
Create Date: 2020-01-14 14:46:21.862129

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a2f0126f69b8"
down_revision = "2ab5564cfe99"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "redirect",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("redirect_path", sa.String(), nullable=False),
        sa.Column("target_url", sa.String(), nullable=False),
        sa.Column("permanent", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("redirect")
