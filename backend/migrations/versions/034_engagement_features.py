"""SPEC-050/051/052: privacidade do benchmark, conquistas, tour e novos tipos de notificação."""

import sqlalchemy as sa
from alembic import op

revision = "034_engagement_features"
down_revision = "033_tax_estimates"
branch_labels = None
depends_on = None

OLD_KINDS = (
    "kind IN ('invoice_due', 'budget_goal_exceeded', 'watchlist_document', 'recurring_expense_due')"
)
NEW_KINDS = (
    "kind IN ('invoice_due', 'budget_goal_exceeded', 'watchlist_document', "
    "'recurring_expense_due', 'achievement_unlocked', 'monthly_summary')"
)
CONSTRAINTS = (
    ("notifications", "valid_notification_kind"),
    ("notification_preferences", "valid_notification_preference_kind"),
)


def upgrade():
    for table, name in CONSTRAINTS:
        op.drop_constraint(name, table, type_="check")
        op.create_check_constraint(name, table, NEW_KINDS)
    op.create_table(
        "privacy_settings",
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("score_benchmark_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "achievements",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "code", name="uq_achievement_user_code"),
    )
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])
    op.create_table(
        "onboarding_tours",
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("step", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'skipped')",
            name="valid_tour_status",
        ),
    )


def downgrade():
    op.drop_table("onboarding_tours")
    op.drop_table("achievements")
    op.drop_table("privacy_settings")
    for table, name in CONSTRAINTS:
        op.execute(f"DELETE FROM {table} WHERE kind IN ('achievement_unlocked', 'monthly_summary')")
        op.drop_constraint(name, table, type_="check")
        op.create_check_constraint(name, table, OLD_KINDS)
