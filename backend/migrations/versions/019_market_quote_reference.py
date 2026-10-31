"""Create the local, explicitly non-real-time market reference for SPEC-023."""

from datetime import UTC, date, datetime

import sqlalchemy as sa
from alembic import op

revision = "019_market_quote_reference"
down_revision = "018_cvm_cache_purge_runs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "market_quotes",
        sa.Column("ticker", sa.String(12), primary_key=True),
        sa.Column("asset_kind", sa.String(12), nullable=False),
        sa.Column("price", sa.Numeric(18, 4), nullable=False),
        sa.Column("previous_close", sa.Numeric(18, 4), nullable=False),
        sa.Column("referenced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("availability", sa.String(12), nullable=False, server_default="available"),
        sa.Column("source_name", sa.String(180), nullable=False),
        sa.CheckConstraint("asset_kind IN ('stock', 'fii')", name="valid_market_asset_kind"),
        sa.CheckConstraint(
            "availability IN ('available', 'unavailable')", name="valid_market_availability"
        ),
    )
    op.create_table(
        "market_quote_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "ticker",
            sa.String(12),
            sa.ForeignKey("market_quotes.ticker", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quoted_on", sa.Date(), nullable=False),
        sa.Column("close_price", sa.Numeric(18, 4), nullable=False),
        sa.UniqueConstraint("ticker", "quoted_on", name="uq_market_quote_history_day"),
    )
    op.create_index("ix_market_quote_history_ticker", "market_quote_history", ["ticker"])
    quotes = sa.table(
        "market_quotes",
        sa.column("ticker", sa.String()),
        sa.column("asset_kind", sa.String()),
        sa.column("price", sa.Numeric()),
        sa.column("previous_close", sa.Numeric()),
        sa.column("referenced_at", sa.DateTime(timezone=True)),
        sa.column("availability", sa.String()),
        sa.column("source_name", sa.String()),
    )
    history = sa.table(
        "market_quote_history",
        sa.column("id", sa.Uuid()),
        sa.column("ticker", sa.String()),
        sa.column("quoted_on", sa.Date()),
        sa.column("close_price", sa.Numeric()),
    )
    reference = datetime(2026, 10, 29, 12, tzinfo=UTC)
    op.bulk_insert(
        quotes,
        [
            {
                "ticker": "PETR4",
                "asset_kind": "stock",
                "price": "31.2500",
                "previous_close": "30.8000",
                "referenced_at": reference,
                "availability": "available",
                "source_name": "Catálogo local de referência FinNova",
            },
            {
                "ticker": "MXRF11",
                "asset_kind": "fii",
                "price": "10.2400",
                "previous_close": "10.1800",
                "referenced_at": reference,
                "availability": "available",
                "source_name": "Catálogo local de referência FinNova",
            },
            {
                "ticker": "FAIL11",
                "asset_kind": "fii",
                "price": "0.0000",
                "previous_close": "0.0000",
                "referenced_at": reference,
                "availability": "unavailable",
                "source_name": "Catálogo local de referência FinNova",
            },
        ],
    )
    op.bulk_insert(
        history,
        [
            {
                "id": "33333333-1111-4000-8000-000000000001",
                "ticker": "PETR4",
                "quoted_on": date(2026, 10, 24),
                "close_price": "30.0200",
            },
            {
                "id": "33333333-1111-4000-8000-000000000002",
                "ticker": "PETR4",
                "quoted_on": date(2026, 10, 27),
                "close_price": "30.4500",
            },
            {
                "id": "33333333-1111-4000-8000-000000000003",
                "ticker": "PETR4",
                "quoted_on": date(2026, 10, 28),
                "close_price": "30.8000",
            },
            {
                "id": "33333333-1111-4000-8000-000000000004",
                "ticker": "PETR4",
                "quoted_on": date(2026, 10, 29),
                "close_price": "31.2500",
            },
            {
                "id": "33333333-1111-4000-8000-000000000005",
                "ticker": "MXRF11",
                "quoted_on": date(2026, 10, 24),
                "close_price": "10.0900",
            },
            {
                "id": "33333333-1111-4000-8000-000000000006",
                "ticker": "MXRF11",
                "quoted_on": date(2026, 10, 27),
                "close_price": "10.1600",
            },
            {
                "id": "33333333-1111-4000-8000-000000000007",
                "ticker": "MXRF11",
                "quoted_on": date(2026, 10, 28),
                "close_price": "10.1800",
            },
            {
                "id": "33333333-1111-4000-8000-000000000008",
                "ticker": "MXRF11",
                "quoted_on": date(2026, 10, 29),
                "close_price": "10.2400",
            },
        ],
    )


def downgrade():
    op.drop_index("ix_market_quote_history_ticker", table_name="market_quote_history")
    op.drop_table("market_quote_history")
    op.drop_table("market_quotes")
