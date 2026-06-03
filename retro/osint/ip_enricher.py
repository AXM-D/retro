from __future__ import annotations

import asyncio
from typing import Any

from retro.core.config import config
from retro.core.exceptions import OSINTError
from retro.osint.base import BaseEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class IPEnricher(BaseEnricher):
    async def enrich(self, ip: str) -> dict:
        result = {"ip": ip, "sources": {}}
        try:
            from taq.connectors.registry import connector_registry
            tasks = []
            connectors_to_try = ["geoip", "whois", "dns_resolver", "shodan_free", "virustotal_free", "abuseipdb"]
            for name in connectors_to_try:
                conn = connector_registry.get(name)
                if conn:
                    if name == "geoip":
                        tasks.append(conn.call("lookup", {"ip": ip}))
                    elif name == "whois":
                        tasks.append(conn.call("ip", {"ip": ip}))
                    elif name == "dns_resolver":
                        tasks.append(conn.call("reverse", {"ip": ip}))
                    elif name in ("shodan_free", "virustotal_free", "abuseipdb"):
                        tasks.append(conn.call("ip", {"ip": ip}))

            if tasks:
                outcomes = await asyncio.gather(*tasks, return_exceptions=True)
                for idx, name in enumerate([n for n in connectors_to_try if connector_registry.get(n)]):
                    if idx < len(outcomes):
                        o = outcomes[idx]
                        if isinstance(o, Exception):
                            result["sources"][name] = {"error": str(o)}
                        elif o and hasattr(o, "to_dict"):
                            result["sources"][name] = o.to_dict()
                        elif o and isinstance(o, dict):
                            result["sources"][name] = o

            result["confidence"] = self._calculate_confidence(result["sources"])
            return result
        except ImportError:
            raise OSINTError("taq-engine not available for IP enrichment")
        except Exception as e:
            raise OSINTError(f"IP enrichment failed: {e}")

    def _calculate_confidence(self, sources: dict) -> float:
        score = 0.0
        if sources.get("geoip", {}).get("success"):
            score += 0.25
        if sources.get("abuseipdb", {}).get("success"):
            data = sources["abuseipdb"].get("data", {})
            if data.get("abuse_confidence_score", 0) > 50:
                score += 0.3
        if sources.get("virustotal_free", {}).get("success"):
            data = sources["virustotal_free"].get("data", {})
            if data.get("malicious", 0) > 0:
                score += 0.3
        if sources.get("shodan_free", {}).get("success"):
            data = sources["shodan_free"].get("data", {})
            if data.get("ports"):
                score += 0.15
        return min(score, 1.0)
