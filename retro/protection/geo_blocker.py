from __future__ import annotations

import asyncio

from retro.utils.logger import get_logger

logger = get_logger(__name__)


class GeoBlocker:
    def __init__(self):
        self._blocked_countries: set[str] = set()

    def block_country(self, country_code: str):
        self._blocked_countries.add(country_code.upper())
        logger.info(f"GeoBlocker: Blocking country {country_code}")

    def unblock_country(self, country_code: str):
        self._blocked_countries.discard(country_code.upper())

    async def is_blocked(self, ip: str) -> bool:
        if not self._blocked_countries:
            return False
        try:
            from taq.connectors.registry import connector_registry
            geo = connector_registry.get("geoip")
            if geo:
                result = await geo.call("lookup", {"ip": ip})
                data = getattr(result, "data", {}) if hasattr(result, "to_dict") else (result or {})
                country = data.get("country_code", "")
                return country.upper() in self._blocked_countries
        except Exception:
            pass
        return False

    def get_blocked_countries(self) -> list[str]:
        return sorted(self._blocked_countries)


geo_blocker = GeoBlocker()
