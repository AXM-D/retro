from __future__ import annotations

from retro.osint.base import BaseEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class HashEnricher(BaseEnricher):
    async def enrich(self, h: str) -> dict:
        result = {"hash": h, "sources": {}}
        try:
            from taq.connectors.registry import connector_registry
            vt = connector_registry.get("virustotal_free")
            if vt:
                resp = await vt.call("hash", {"hash": h})
                result["sources"]["virustotal"] = resp.to_dict() if hasattr(resp, "to_dict") else resp
        except Exception as e:
            result["error"] = str(e)

        result["malware_bazaar"] = await self._check_malware_bazaar(h)
        return result

    async def _check_malware_bazaar(self, h: str) -> dict:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://mb-api.abuse.ch/api/v1/",
                    data={"query": "get_info", "hash": h},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("query_status") == "ok":
                        entries = data.get("data", [])
                        if entries:
                            e = entries[0]
                            return {
                                "found": True,
                                "file_name": e.get("file_name"),
                                "file_type": e.get("file_type"),
                                "signature": e.get("signature"),
                                "first_seen": e.get("first_seen"),
                                "tags": e.get("tags", []),
                            }
                    return {"found": False}
                return {"found": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"found": False, "error": str(e)}
