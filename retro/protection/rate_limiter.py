from __future__ import annotations

import time
from collections import defaultdict

from retro.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self._counts: dict[str, list[float]] = defaultdict(list)
        self._max_requests = max_requests
        self._window = window

    def is_rate_limited(self, ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - self._window
        self._counts[ip] = [t for t in self._counts[ip] if t > cutoff]
        if len(self._counts[ip]) >= self._max_requests:
            return True
        self._counts[ip].append(now)
        return False

    def get_count(self, ip: str) -> int:
        cutoff = time.monotonic() - self._window
        self._counts[ip] = [t for t in self._counts[ip] if t > cutoff]
        return len(self._counts[ip])


rate_limiter = RateLimiter()
