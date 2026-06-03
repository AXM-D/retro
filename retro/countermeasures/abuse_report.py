from __future__ import annotations

from retro.countermeasures.base import BaseCountermeasure
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class AbuseReport(BaseCountermeasure):
    def name(self) -> str:
        return "abuse_report"

    async def execute(self, target: str, target_type: str = "ip", **kwargs) -> dict:
        results = {}
        if target_type == "ip":
            results["abuseipdb"] = await self._report_abuseipdb(target, kwargs.get("comment", ""))
        elif target_type == "domain":
            results["spamhaus"] = await self._report_spamhaus(target)
        results["summary"] = "reported" if any(r.get("status") == "reported" for r in results.values()) else "failed"
        return results

    async def dry_run(self, target: str, target_type: str = "ip") -> dict:
        if target_type == "ip":
            return {"would_report": ["abuseipdb", "spamhaus"], "target": target}
        return {"would_report": ["spamhaus"], "target": target}

    async def _report_abuseipdb(self, ip: str, comment: str = "") -> dict:
        try:
            from taq.connectors.registry import connector_registry
            abuse = connector_registry.get("abuseipdb")
            if abuse:
                result = await abuse.call("report", {"ip": ip, "comment": comment or "Reported by RETRO - Active Defense"})
                if hasattr(result, "to_dict"):
                    return result.to_dict()
                return {"status": "reported", "source": "abuseipdb"}
            return {"status": "not_configured", "source": "abuseipdb"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _report_spamhaus(self, domain: str) -> dict:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://check.spamhaus.org/api/v1/report/",
                    json={"domain": domain},
                )
                return {"status": "reported" if resp.status_code == 200 else "failed", "source": "spamhaus"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
