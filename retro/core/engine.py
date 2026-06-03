from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable, Optional
from uuid import uuid4

from retro.core.config import config
from retro.core.exceptions import RetroError
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class AttackEvent:
    def __init__(self, sensor: str, event_type: str, source_ip: str, **kwargs):
        self.id: str = uuid4().hex[:12]
        self.sensor = sensor
        self.event_type = event_type
        self.source_ip = source_ip
        self.timestamp: datetime = datetime.utcnow()
        self.data: dict = kwargs
        self.processed: bool = False
        self.threat_score: float = 0.0
        self.investigation_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sensor": self.sensor,
            "event_type": self.event_type,
            "source_ip": self.source_ip,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "processed": self.processed,
            "threat_score": self.threat_score,
            "investigation_id": self.investigation_id,
        }


class AttackerProfile:
    def __init__(self, ip: str):
        self.ip = ip
        self.first_seen: datetime = datetime.utcnow()
        self.last_seen: datetime = datetime.utcnow()
        self.total_events: int = 1
        self.event_types: set[str] = set()
        self.tags: list[str] = []
        self.osint_data: dict = {}
        self.threat_score: float = 0.0
        self.blocked: bool = False
        self.reported: bool = False

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "total_events": self.total_events,
            "event_types": list(self.event_types),
            "tags": self.tags,
            "osint_data": self.osint_data,
            "threat_score": self.threat_score,
            "blocked": self.blocked,
            "reported": self.reported,
        }


class RetroEngine:
    def __init__(self):
        self._events: dict[str, AttackEvent] = {}
        self._attackers: dict[str, AttackerProfile] = {}
        self._sensors: dict[str, Any] = {}
        self._event_callbacks: list[Callable] = []
        self._running: bool = False

    def register_sensor(self, name: str, sensor: Any):
        self._sensors[name] = sensor

    def on_event(self, callback: Callable):
        self._event_callbacks.append(callback)

    async def ingest_event(self, sensor: str, event_type: str, source_ip: str, **kwargs) -> AttackEvent:
        event = AttackEvent(sensor, event_type, source_ip, **kwargs)
        self._events[event.id] = event
        self._update_attacker(source_ip, event_type)
        logger.info(f"Event ingested: {event_type} from {source_ip} via {sensor}")
        for cb in self._event_callbacks:
            asyncio.ensure_future(cb(event))
        return event

    def _update_attacker(self, ip: str, event_type: str):
        if ip not in self._attackers:
            self._attackers[ip] = AttackerProfile(ip)
        profile = self._attackers[ip]
        profile.last_seen = datetime.utcnow()
        profile.total_events += 1
        profile.event_types.add(event_type)

    async def run_osint(self, event_id: str, playbook_name: str = "ip_full_investigation") -> Optional[dict]:
        event = self._events.get(event_id)
        if not event:
            return None
        try:
            from taq.core.engine import engine
            inv = await engine.create_investigation(
                seed_type="ip",
                seed_value=event.source_ip,
                playbook_id=playbook_name,
                metadata={"event_id": event_id, "sensor": event.sensor},
            )
            result = await engine.run_investigation(inv.id)
            event.processed = True
            event.investigation_id = inv.id
            profile = self._attackers.get(event.source_ip)
            if profile:
                profile.osint_data = result.results
            return result.results
        except Exception as e:
            logger.error(f"OSINT run failed for {event_id}: {e}")
            return None

    async def get_events(self, limit: int = 100) -> list[AttackEvent]:
        return sorted(self._events.values(), key=lambda e: e.timestamp, reverse=True)[:limit]

    async def get_attackers(self) -> list[AttackerProfile]:
        return list(self._attackers.values())

    async def get_attacker(self, ip: str) -> Optional[AttackerProfile]:
        return self._attackers.get(ip)

    async def get_stats(self) -> dict:
        return {
            "total_events": len(self._events),
            "unique_attackers": len(self._attackers),
            "blocked_attackers": sum(1 for a in self._attackers.values() if a.blocked),
            "reported_attackers": sum(1 for a in self._attackers.values() if a.reported),
        }

    async def start_sensors(self):
        self._running = True
        for name, sensor in self._sensors.items():
            asyncio.ensure_future(sensor.start(self.ingest_event))
            logger.info(f"Sensor started: {name}")

    async def stop_sensors(self):
        self._running = False
        for name, sensor in self._sensors.items():
            try:
                await sensor.stop()
                logger.info(f"Sensor stopped: {name}")
            except Exception as e:
                logger.warning(f"Error stopping sensor {name}: {e}")


engine = RetroEngine()
