"""Persist SPEC-027 personal company watchlists."""

import sqlalchemy as sa
from alembic import op

revision = "025_watchlist"
down_revision = "024_foreign_currency"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "watchlist",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "company_id",
            sa.Uuid(),
            sa.ForeignKey("public_companies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "company_id", name="uq_watchlist_owner_company"),
    )


def downgrade():
    op.drop_table("watchlist")
