from __future__ import annotations

import asyncio
import re

from retro.osint.base import BaseEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class EmailEnricher(BaseEnricher):
    async def enrich(self, email: str) -> dict:
        result = {"email": email, "sources": {}}
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            result["valid"] = False
            return result
        result["valid"] = True
        domain = email.split("@")[1]
        result["domain"] = domain
        try:
            from taq.connectors.registry import connector_registry
            dns = connector_registry.get("dns_resolver")
            if dns:
                mx = await dns.call("mx", {"domain": domain})
                result["sources"]["dns"] = mx.to_dict() if hasattr(mx, "to_dict") else mx
        except Exception:
            pass
        result["breaches"] = await self._check_breaches(email)
        return result

    async def _check_breaches(self, email: str) -> list[dict]:
        breaches = []
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={"hibp-api-key": "", "user-agent": "Retro-OSINT"},
                )
                if resp.status_code == 200:
                    for b in resp.json():
                        breaches.append({"name": b.get("Name"), "date": b.get("BreachDate"), "data_classes": b.get("DataClasses", [])})
        except Exception:
            pass
        return breaches
