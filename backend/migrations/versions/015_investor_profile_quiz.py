"""Persist the investor profile calculated by SPEC-003's quiz."""

import sqlalchemy as sa
from alembic import op

revision = "015_investor_profile_quiz"
down_revision = "014_admin_users_metadata"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("investor_profile", sa.String(20), nullable=True))
    op.create_check_constraint(
        "valid_investor_profile",
        "users",
        "investor_profile IN ('conservador', 'moderado', 'arrojado') OR investor_profile IS NULL",
    )


def downgrade():
    op.drop_constraint("valid_investor_profile", "users", type_="check")
    op.drop_column("users", "investor_profile")
