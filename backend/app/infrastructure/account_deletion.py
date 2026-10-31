"""Deletion tombstones must live outside PostgreSQL backups and be preserved on restore."""

import hashlib
import hmac
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.infrastructure.models import (
    AuditLogRecord,
    Base,
    LoginAttemptRecord,
    UsageEventRecord,
    UserRecord,
)
from app.infrastructure.security import Security


class DeletionJournal:
    def __init__(self, path: str, key: str):
        self.path, self.key = Path(path), key.encode()

    def digest(self, user_id: uuid.UUID) -> str:
        return hmac.new(
            self.key, f"account-deletion:{user_id}".encode(), hashlib.sha256
        ).hexdigest()

    @contextmanager
    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        db = sqlite3.connect(self.path, timeout=10)
        self.path.chmod(0o600)
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("CREATE TABLE IF NOT EXISTS deletions (digest TEXT PRIMARY KEY)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS audit "
                "(action TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )
            with db:
                yield db
        finally:
            db.close()

    def contains(self, user_id: uuid.UUID) -> bool:
        if not self.path.exists():
            raise OSError("Missing independent deletion journal")
        with self.connect() as db:
            return (
                db.execute(
                    "SELECT 1 FROM deletions WHERE digest = ?", (self.digest(user_id),)
                ).fetchone()
                is not None
            )

    def record(self, user_id: uuid.UUID) -> None:
        with self.connect() as db:
            inserted = db.execute(
                "INSERT OR IGNORE INTO deletions VALUES (?)", (self.digest(user_id),)
            )
            if inserted.rowcount:
                db.execute("INSERT INTO audit (action) VALUES ('account_deletion_requested')")

    def apply(self, db: Session) -> None:
        if not self.path.exists() and db.scalar(select(UserRecord.id).limit(1)) is not None:
            raise OSError("Missing independent deletion journal; restore is not safe")
        with self.connect() as journal:
            digests = {row[0] for row in journal.execute("SELECT digest FROM deletions")}
        for user_id in db.scalars(select(UserRecord.id)):
            if self.digest(user_id) in digests:
                security = Security(self.key.decode())
                user = db.get(UserRecord, user_id)
                email = security.decrypt(user.email_encrypted)
                db.execute(
                    delete(LoginAttemptRecord).where(
                        LoginAttemptRecord.email_key == security.lookup(f"login-attempt:{email}")
                    )
                )
                erase_user(db, user_id)
        db.commit()


def erase_user(db: Session, user_id: uuid.UUID) -> None:
    # Delete dependents before accounts/cards to respect expense RESTRICT constraints.
    # SPEC-060 keeps aggregate/audit evidence while breaking the link to the person.
    db.execute(
        update(UsageEventRecord).where(UsageEventRecord.user_id == user_id).values(user_id=None)
    )
    db.execute(update(AuditLogRecord).where(AuditLogRecord.user_id == user_id).values(user_id=None))
    for table in reversed(Base.metadata.sorted_tables):
        if table.name in {"users", "usage_events", "audit_logs"}:
            continue
        for column in table.columns:
            if any(fk.target_fullname == "users.id" for fk in column.foreign_keys):
                db.execute(delete(table).where(column == user_id))
    db.execute(delete(UserRecord).where(UserRecord.id == user_id))
