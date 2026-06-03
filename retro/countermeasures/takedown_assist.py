from __future__ import annotations

from datetime import datetime

from retro.countermeasures.base import BaseCountermeasure
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class TakedownAssist(BaseCountermeasure):
    def name(self) -> str:
        return "takedown_assist"

    async def execute(self, target: str, target_type: str = "url", **kwargs) -> dict:
        evidence = kwargs.get("evidence", "")
        report_type = "phishing" if "phish" in kwargs.get("tags", "").lower() else "abuse"
        template = self._generate_template(target, target_type, report_type, evidence)
        output = f"""TAKEDOWN REPORT - {datetime.utcnow().isoformat()}
{'='*60}

Target: {target}
Type: {target_type}
Report Type: {report_type}

Description:
{template}

Evidence:
{evidence[:2000] if evidence else 'See attached OSINT data'}

Actions to take:
1. Report to hosting provider abuse contact
2. Report to domain registrar
3. Report to relevant CERT/CSIRT
4. If phishing: report to APWG (reportphishing@apwg.org)
5. If malware: report to MalwareBazaar
"""
        return {
            "status": "generated",
            "report": output,
            "actions": [
                "Report to hosting provider",
                "Report to domain registrar",
                "Report to CERT/CSIRT",
            ],
        }

    async def dry_run(self, target: str, target_type: str = "url") -> dict:
        return {"would_generate": "takedown_report", "target": target}

    def _generate_template(self, target: str, target_type: str, report_type: str, evidence: str) -> str:
        return f"""This is a report regarding a {report_type} incident involving:
- Target: {target}
- Type: {target_type}

The identified resource is being used for malicious purposes. We request immediate investigation and takedown.

Thank you."""
