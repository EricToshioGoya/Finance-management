"""Add personal categories and per-user default visibility.

Revision ID: 007_categories
Revises: 006_password_reset
"""

import sqlalchemy as sa
from alembic import op

revision = "007_categories"
down_revision = "006_password_reset"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("name_lookup", sa.String(length=64), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="valid_category_color"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name_lookup", name="uq_categories_user_name_lookup"),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])
    op.create_table(
        "default_category_visibility",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_key", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "category_key"),
    )


def downgrade():
    op.drop_table("default_category_visibility")
    op.drop_table("categories")
