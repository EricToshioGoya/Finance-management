"""SPEC-041: owner-managed grants and separate, read-only consumer credentials."""

import secrets
import uuid
from datetime import timedelta
from hmac import compare_digest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.auth import AuthError, AuthService
from app.infrastructure.models import ExternalApiKeyRecord, UserRecord
from app.infrastructure.security import Security, token_digest

GRANTED_SCOPES = frozenset({"balance:read", "net_worth:read"})
EXTERNAL_REQUESTS_PER_MINUTE = 30
MAX_KEY_LIFETIME_DAYS = 90


class ExternalApiService:
    def __init__(self, db: Session, security: Security, auth: AuthService):
        self.db = db
        self.security = security
        self.auth = auth

    def _output(self, record: ExternalApiKeyRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "name": self.security.decrypt(record.name_encrypted),
            "scopes": sorted(record.scopes.split(",")),
            "created_at": record.created_at,
            "expires_at": record.expires_at,
            "revoked_at": record.revoked_at,
            "last_used_at": record.last_used_at,
        }

    def list_grants(self, owner_id: uuid.UUID) -> list[dict[str, object]]:
        self.auth.require_category_owner(owner_id)
        grants = self.db.scalars(
            select(ExternalApiKeyRecord)
            .where(ExternalApiKeyRecord.user_id == owner_id)
            .order_by(ExternalApiKeyRecord.created_at, ExternalApiKeyRecord.id)
        ).all()
        return [self._output(grant) for grant in grants]

    def create_grant(self, owner_id: uuid.UUID, name: str, scopes: list[str]) -> dict[str, object]:
        self.auth.require_category_owner(owner_id)
        if not scopes or len(scopes) != len(set(scopes)) or not set(scopes) <= GRANTED_SCOPES:
            raise AuthError("invalid_external_scope", 422)
        now = self.auth.clock()
        secret = "fnv_" + secrets.token_urlsafe(32)
        grant = ExternalApiKeyRecord(
            user_id=owner_id,
            name_encrypted=self.security.encrypt(name),
            key_digest=token_digest(secret),
            scopes=",".join(sorted(scopes)),
            created_at=now,
            expires_at=now + timedelta(days=MAX_KEY_LIFETIME_DAYS),
            request_count=0,
        )
        self.db.add(grant)
        self.db.commit()
        self.db.refresh(grant)
        return {**self._output(grant), "api_key": secret}

    def revoke_grant(self, owner_id: uuid.UUID, grant_id: uuid.UUID) -> None:
        self.auth.require_category_owner(owner_id)
        grant = self.db.scalar(
            select(ExternalApiKeyRecord)
            .where(
                ExternalApiKeyRecord.id == grant_id,
                ExternalApiKeyRecord.user_id == owner_id,
            )
            .with_for_update()
        )
        if grant is None:
            raise AuthError("external_key_not_found", 404)
        if grant.revoked_at is None:
            grant.revoked_at = self.auth.clock()
        self.db.commit()

    def consume(self, raw_key: str | None, needed_scope: str) -> uuid.UUID:
        """Lock the persisted key row: quotas remain effective across workers."""
        if (
            raw_key is None
            or len(raw_key) > 100
            or not raw_key.startswith("fnv_")
            or needed_scope not in GRANTED_SCOPES
        ):
            raise AuthError("invalid_external_key")
        grant = self.db.scalar(
            select(ExternalApiKeyRecord)
            .where(ExternalApiKeyRecord.key_digest == token_digest(raw_key))
            .with_for_update()
        )
        if grant is None or not compare_digest(grant.key_digest, token_digest(raw_key)):
            raise AuthError("invalid_external_key")
        now = self.auth.clock()
        owner = self.db.get(UserRecord, grant.user_id)
        if (
            grant.revoked_at is not None
            or now >= grant.expires_at
            or owner is None
            or owner.email_verified_at is None
        ):
            raise AuthError("invalid_external_key")
        if needed_scope not in grant.scopes.split(","):
            raise AuthError("external_scope_denied", 403)
        if grant.window_started_at is None or now >= grant.window_started_at + timedelta(minutes=1):
            grant.window_started_at = now
            grant.request_count = 0
        if grant.request_count >= EXTERNAL_REQUESTS_PER_MINUTE:
            raise AuthError("external_rate_limit", 429, retry_after=60)
        grant.request_count += 1
        grant.last_used_at = now
        self.db.commit()
        return owner.id
