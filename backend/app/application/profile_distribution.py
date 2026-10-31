"""SPEC-062: distribuição agregada de perfis de investidor para administradores."""

from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from app.application.auth import AuthError, AuthService
from app.infrastructure.models import UserRecord

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
PROFILES = ("conservador", "moderado", "arrojado")


class ProfileDistributionService:
    def __init__(self, db, auth: AuthService):
        self.db, self.auth = db, auth

    def distribution(self, actor, start: date | None, end: date | None) -> dict[str, object]:
        # R02/R04: somente administrador; período de cadastro inclusivo no fuso de São Paulo.
        self.auth.require_admin(actor)
        if start and end and start > end:
            raise AuthError("invalid_period", 422)
        query = select(UserRecord.investor_profile, func.count()).group_by(
            UserRecord.investor_profile
        )
        if start:
            query = query.where(
                UserRecord.created_at >= datetime.combine(start, time.min, tzinfo=SAO_PAULO)
            )
        if end:
            query = query.where(
                UserRecord.created_at
                < datetime.combine(end + timedelta(days=1), time.min, tzinfo=SAO_PAULO)
            )
        counts = {profile: total for profile, total in self.db.execute(query).all()}
        profiled = sum(counts.get(profile, 0) for profile in PROFILES)
        # INV-001: somente contagens agregadas; conta sem quiz fica em "sem perfil".
        items = [
            {
                "profile": profile,
                "count": counts.get(profile, 0),
                "percentage": (Decimal(counts.get(profile, 0) * 100) / Decimal(profiled)).quantize(
                    Decimal("0.01"), ROUND_HALF_EVEN
                )
                if profiled
                else Decimal("0.00"),
            }
            for profile in PROFILES
        ]
        return {
            "start": start,
            "end": end,
            "total_users": sum(counts.values()),
            "profiled_users": profiled,
            "without_profile": counts.get(None, 0),
            "items": items,
            "generated_at": self.auth.clock(),
        }
