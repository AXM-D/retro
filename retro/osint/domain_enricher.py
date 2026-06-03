from __future__ import annotations

import asyncio
from typing import Any

from retro.osint.base import BaseEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class DomainEnricher(BaseEnricher):
    async def enrich(self, domain: str) -> dict:
        result = {"domain": domain, "sources": {}}
        try:
            from taq.connectors.registry import connector_registry
            tasks = []
            names = []
            for name in ["dns_resolver", "whois", "virustotal_free"]:
                conn = connector_registry.get(name)
                if conn:
                    names.append(name)
                    if name == "dns_resolver":
                        tasks.append(asyncio.gather(
                            conn.call("resolve", {"hostname": domain}),
                            conn.call("mx", {"domain": domain}),
                            conn.call("txt", {"domain": domain}),
                            return_exceptions=True,
                        ))
                    elif name == "whois":
                        tasks.append(conn.call("lookup", {"domain": domain}))
                    elif name == "virustotal_free":
                        tasks.append(conn.call("domain", {"domain": domain}))

            for idx, name in enumerate(names):
                if idx < len(tasks):
                    o = tasks[idx]
                    if isinstance(o, list):
                        continue
                    o = await o
                    if hasattr(o, "to_dict"):
                        result["sources"][name] = o.to_dict() if hasattr(o, "to_dict") else o
        except Exception:
            pass
        return result
