from collections import defaultdict
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.application.auth import AuthError, AuthService
from app.infrastructure.models import UsageEventRecord, UserRecord


class EngagementService:
    def __init__(self, db, auth: AuthService):
        self.db, self.auth = db, auth

    def report(self, actor, start: date | None, end: date | None, inactive_days: int):
        self.auth.require_admin(actor)
        end = end or self.auth.clock().date()
        start = start or end - timedelta(days=29)
        if start > end or (end - start).days > 365:
            raise AuthError("invalid_engagement_period", 422)
        tz = self.auth.clock().tzinfo
        events = self.db.execute(
            select(
                UsageEventRecord.user_id, UsageEventRecord.module, UsageEventRecord.occurred_at
            ).where(
                UsageEventRecord.occurred_at >= datetime.combine(start, time.min, tzinfo=tz),
                UsageEventRecord.occurred_at
                < datetime.combine(end + timedelta(days=1), time.min, tzinfo=tz),
            )
        ).all()
        mods = {}
        daily = defaultdict(set)
        per = defaultdict(int)
        active = set()
        for uid, module, at in events:
            r = mods.setdefault(module, {"accesses": 0, "users": set()})
            r["accesses"] += 1
            if uid is not None:
                r["users"].add(uid)
                daily[at.date()].add(uid)
                per[(uid, module)] += 1
                active.add(uid)
        modules = [
            {"module": m, "accesses": r["accesses"], "unique_users": len(r["users"])}
            for m, r in sorted(mods.items())
        ]
        rank = sorted(modules, key=lambda r: (-r["accesses"], r["module"]))
        least = sorted(modules, key=lambda r: (r["accesses"], r["module"]))

        def metric(n):
            return len(
                {
                    uid
                    for uid, _, at in events
                    if uid is not None and at.date() >= end - timedelta(days=n - 1)
                }
            )

        all_users = set(self.db.scalars(select(UserRecord.id)).all())
        cut = end - timedelta(days=inactive_days)
        recent = set(
            self.db.scalars(
                select(UsageEventRecord.user_id).where(
                    UsageEventRecord.user_id.is_not(None),
                    UsageEventRecord.occurred_at > datetime.combine(cut, time.max, tzinfo=tz),
                )
            ).all()
        )
        recur = defaultdict(int)
        for (_, m), n in per.items():
            if n >= 2:
                recur[m] += 1
        trend = []
        d = start
        while d <= end:
            trend.append(
                {
                    "date": d,
                    "accesses": sum(1 for _, _, at in events if at.date() == d),
                    "unique_users": len(daily[d]),
                }
            )
            d += timedelta(days=1)
        return {
            "start": start,
            "end": end,
            "modules": modules,
            "most_used_module": rank[0]["module"] if rank else None,
            "least_used_module": least[0]["module"] if least else None,
            "dau": metric(1),
            "wau": metric(7),
            "mau": metric(30),
            "average_frequency": len(events) / len(active) if active else 0,
            "inactive_users": len(all_users - recent),
            "inactive_days": inactive_days,
            "recurring_modules": [
                {"module": m, "recurring_users": n} for m, n in sorted(recur.items())
            ],
            "trend": trend,
        }
