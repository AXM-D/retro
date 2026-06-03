from __future__ import annotations

from typing import Optional

from retro.osint.ip_enricher import IPEnricher
from retro.osint.email_enricher import EmailEnricher
from retro.osint.domain_enricher import DomainEnricher
from retro.osint.hash_enricher import HashEnricher
from retro.osint.user_enricher import UsernameEnricher
from retro.osint.phone_enricher import PhoneEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class ProfileBuilder:
    def __init__(self):
        self.enrichers = {
            "ip": IPEnricher(),
            "email": EmailEnricher(),
            "domain": DomainEnricher(),
            "hash": HashEnricher(),
            "username": UsernameEnricher(),
            "phone": PhoneEnricher(),
        }

    async def build(self, entity_type: str, entity_value: str) -> dict:
        profile = {
            "entity_type": entity_type,
            "entity_value": entity_value,
            "data": {},
            "related": [],
        }
        enricher = self.enrichers.get(entity_type)
        if enricher:
            try:
                data = await enricher.enrich(entity_value)
                profile["data"] = data
            except Exception as e:
                logger.error(f"Profile build failed for {entity_type}:{entity_value}: {e}")
                profile["error"] = str(e)
        if entity_type == "ip":
            related_email = None
            profile["related"] = [r for r in [related_email] if r]
        return profile
