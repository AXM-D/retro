from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseEnricher(ABC):
    @abstractmethod
    async def enrich(self, value: str) -> dict:
        ...
