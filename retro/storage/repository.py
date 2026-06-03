from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from retro.storage.models import AttackEventModel, AttackerModel, CountermeasureModel, AlertModel


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_attack_event(self, event: AttackEventModel) -> AttackEventModel:
        self.session.add(event)
        await self.session.commit()
        return event

    async def get_attack_events(self, limit: int = 100, offset: int = 0) -> list[AttackEventModel]:
        q = select(AttackEventModel).order_by(desc(AttackEventModel.timestamp)).limit(limit).offset(offset)
        return list((await self.session.execute(q)).scalars().all())

    async def count_attack_events(self) -> int:
        r = await self.session.execute(select(func.count(AttackEventModel.id)))
        return r.scalar() or 0

    async def save_attacker(self, a: AttackerModel) -> AttackerModel:
        existing = await self.session.execute(select(AttackerModel).where(AttackerModel.ip == a.ip))
        ex = existing.scalar_one_or_none()
        if ex:
            ex.last_seen = datetime.utcnow()
            ex.total_events += 1
            types_set = set(ex.event_types or [])
            types_set.add(*(a.event_types or []))
            ex.event_types = list(types_set)
            if a.threat_score:
                ex.threat_score = max(ex.threat_score or 0, a.threat_score)
            await self.session.commit()
            return ex
        self.session.add(a)
        await self.session.commit()
        return a

    async def get_attackers(self) -> list[AttackerModel]:
        q = select(AttackerModel).order_by(desc(AttackerModel.last_seen))
        return list((await self.session.execute(q)).scalars().all())

    async def get_attacker(self, ip: str) -> Optional[AttackerModel]:
        r = await self.session.execute(select(AttackerModel).where(AttackerModel.ip == ip))
        return r.scalar_one_or_none()

    async def save_countermeasure(self, cm: CountermeasureModel) -> CountermeasureModel:
        self.session.add(cm)
        await self.session.commit()
        return cm

    async def get_countermeasures(self, limit: int = 50) -> list[CountermeasureModel]:
        q = select(CountermeasureModel).order_by(desc(CountermeasureModel.executed_at)).limit(limit)
        return list((await self.session.execute(q)).scalars().all())

    async def save_alert(self, alert: AlertModel) -> AlertModel:
        self.session.add(alert)
        await self.session.commit()
        return alert

    async def get_alerts(self, limit: int = 50) -> list[AlertModel]:
        q = select(AlertModel).order_by(desc(AlertModel.created_at)).limit(limit)
        return list((await self.session.execute(q)).scalars().all())

    async def get_stats(self) -> dict:
        total_events = (await self.session.execute(select(func.count(AttackEventModel.id)))).scalar() or 0
        total_attackers = (await self.session.execute(select(func.count(AttackerModel.ip)))).scalar() or 0
        blocked = (await self.session.execute(select(func.count(AttackerModel.ip)).where(AttackerModel.blocked == True))).scalar() or 0
        reported = (await self.session.execute(select(func.count(AttackerModel.ip)).where(AttackerModel.reported == True))).scalar() or 0
        return {
            "total_events": total_events,
            "unique_attackers": total_attackers,
            "blocked_attackers": blocked,
            "reported_attackers": reported,
        }

    async def get_dashboard(self) -> dict:
        stats = await self.get_stats()
        recent_events = await self.get_attack_events(limit=10)
        recent_alerts = await self.get_alerts(limit=5)
        return {
            **stats,
            "recent_events": [{"id": e.id, "source_ip": e.source_ip, "event_type": e.event_type, "timestamp": e.timestamp.isoformat() if e.timestamp else ""} for e in recent_events],
            "recent_alerts": [{"id": a.id, "title": a.title, "severity": a.severity, "created_at": a.created_at.isoformat() if a.created_at else ""} for a in recent_alerts],
        }
