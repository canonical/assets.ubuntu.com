"""Add tokens

Revision ID: eb9f8639d610
Revises:
Create Date: 2019-12-09 14:38:26.434966

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb9f8639d610"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("token")
