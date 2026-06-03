from __future__ import annotations

import re

from retro.osint.base import BaseEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class PhoneEnricher(BaseEnricher):
    COUNTRY_CODES = {
        "1": "US/CA", "34": "ES", "44": "UK", "52": "MX",
        "54": "AR", "55": "BR", "57": "CO", "58": "VE",
        "81": "JP", "86": "CN", "91": "IN", "49": "DE",
        "33": "FR", "39": "IT", "7": "RU", "971": "AE",
    }

    async def enrich(self, phone: str) -> dict:
        result = {"phone": phone, "sources": {}}
        cleaned = re.sub(r"[^\d+]", "", phone)
        result["cleaned"] = cleaned
        result["valid"] = len(cleaned) >= 8
        for code, country in sorted(self.COUNTRY_CODES.items(), key=lambda x: -len(x[0])):
            if cleaned.startswith("+" + code) or cleaned.startswith(code):
                result["country"] = country
                break
        return result
