from __future__ import annotations

import asyncio

from retro.utils.logger import get_logger

logger = get_logger(__name__)


class IPReputationChecker:
    def __init__(self):
        self._cache: dict[str, float] = {}

    async def check(self, ip: str) -> float:
        if ip in self._cache:
            return self._cache[ip]
        score = 0.0
        try:
            from taq.connectors.registry import connector_registry
            abuse = connector_registry.get("abuseipdb")
            vt = connector_registry.get("virustotal_free")
            results = await asyncio.gather(
                abuse.call("check", {"ip": ip}) if abuse else None,
                vt.call("ip", {"ip": ip}) if vt else None,
                return_exceptions=True,
            )
            for r in results:
                if isinstance(r, Exception):
                    continue
                data = getattr(r, "data", {}) if hasattr(r, "to_dict") else (r or {})
                if isinstance(data, dict):
                    if "abuse_confidence_score" in data:
                        score += data["abuse_confidence_score"] / 100
                    if "malicious" in data:
                        score += min(data["malicious"] / 10, 0.5)
            score = min(score, 1.0)
        except Exception as e:
            logger.warning(f"Reputation check failed for {ip}: {e}")
        self._cache[ip] = score
        return score


ip_reputation = IPReputationChecker()
