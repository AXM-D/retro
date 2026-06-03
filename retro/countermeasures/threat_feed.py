from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from retro.core.config import config
from retro.countermeasures.base import BaseCountermeasure
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class ThreatFeedGenerator(BaseCountermeasure):
    def name(self) -> str:
        return "threat_feed"

    async def execute(self, target: str, target_type: str = "ip", **kwargs) -> dict:
        score = kwargs.get("score", 50)
        event_type = kwargs.get("event_type", "unknown")
        data_dir = config.retro.data_dir
        output_dir = Path(data_dir) / "threat_feeds"
        output_dir.mkdir(parents=True, exist_ok=True)
        ioc = {
            "type": target_type,
            "value": target,
            "score": score,
            "event_type": event_type,
            "reported_at": datetime.utcnow().isoformat(),
            "source": "RETRO",
        }
        json_path = output_dir / f"iocs_{datetime.utcnow().strftime('%Y%m%d')}.json"
        existing = []
        if json_path.exists():
            existing = json.loads(json_path.read_text())
        existing.append(ioc)
        json_path.write_text(json.dumps(existing, indent=2))
        stix_path = output_dir / f"iocs_{datetime.utcnow().strftime('%Y%m%d')}.stix2"
        stix_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{target[:16]}",
            "pattern": f"[{target_type}:value = '{target}']",
            "pattern_type": "stix",
            "created": datetime.utcnow().isoformat(),
            "modified": datetime.utcnow().isoformat(),
            "confidence": score,
        }
        stix_path.write_text(json.dumps(stix_obj, indent=2))
        logger.info(f"Threat feed updated for {target}")
        return {"status": "exported", "json_path": str(json_path), "stix_path": str(stix_path)}

    async def dry_run(self, target: str, target_type: str = "ip") -> dict:
        return {"would_export": True, "formats": ["json", "stix2"]}
