from __future__ import annotations

from retro.utils.logger import get_logger

logger = get_logger(__name__)


class DNSSinkhole:
    def __init__(self):
        self._blocked_domains: set[str] = set()

    def block_domain(self, domain: str):
        self._blocked_domains.add(domain.lower())
        logger.info(f"DNS Sinkhole: Blocking domain {domain}")

    def unblock_domain(self, domain: str):
        self._blocked_domains.discard(domain.lower())

    def is_blocked(self, domain: str) -> bool:
        domain = domain.lower()
        return domain in self._blocked_domains or any(domain.endswith(f".{d}") for d in self._blocked_domains)

    def get_blocked_domains(self) -> list[str]:
        return sorted(self._blocked_domains)


dns_sinkhole = DNSSinkhole()
