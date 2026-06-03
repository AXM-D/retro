from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseCountermeasure(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def execute(self, target: str, target_type: str, **kwargs) -> dict:
        ...

    @abstractmethod
    async def dry_run(self, target: str, target_type: str) -> dict:
        ...
