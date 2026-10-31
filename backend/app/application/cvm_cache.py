"""SPEC-054 public-CVM cache expiry, with a calendar-year cutoff and aggregated audit."""

from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.infrastructure.models import (
    CvmCachePurgeRunRecord,
    FinancialIndicatorRecord,
    OfficialDocumentRecord,
)


def twelve_calendar_months_before(instant: datetime) -> datetime:
    """Subtract one calendar year, handling the February 29 boundary explicitly."""
    instant = instant.astimezone(UTC)
    try:
        return instant.replace(year=instant.year - 1)
    except ValueError:
        return instant.replace(year=instant.year - 1, day=28)


class CvmCacheService:
    def __init__(self, db: Session, clock: Callable[[], datetime] | None = None):
        self.db = db
        self.clock = clock or (lambda: datetime.now(UTC))

    def purge_expired(self) -> dict[str, int | str | datetime]:
        now = self.clock().astimezone(UTC)
        cutoff = twelve_calendar_months_before(now)
        documents = self.db.execute(
            delete(OfficialDocumentRecord).where(OfficialDocumentRecord.synced_at <= cutoff)
        )
        indicators = self.db.execute(
            delete(FinancialIndicatorRecord).where(FinancialIndicatorRecord.synced_at <= cutoff)
        )
        documents_expunged = int(documents.rowcount or 0)
        indicators_expunged = int(indicators.rowcount or 0)
        self.db.add(
            CvmCachePurgeRunRecord(
                occurred_at=now,
                documents_expunged=documents_expunged,
                indicators_expunged=indicators_expunged,
                status="completed",
            )
        )
        # The audit line and deletes share one transaction, so failure cannot claim success.
        self.db.commit()
        return {
            "occurred_at": now,
            "documents_expunged": documents_expunged,
            "indicators_expunged": indicators_expunged,
            "status": "completed",
        }
