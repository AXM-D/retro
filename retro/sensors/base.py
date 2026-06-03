from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine


class BaseSensor(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def start(self, on_event: Callable[..., Coroutine[Any, Any, Any]]):
        ...

    @abstractmethod
    async def stop(self):
        ...

    @abstractmethod
    def is_running(self) -> bool:
        ...
