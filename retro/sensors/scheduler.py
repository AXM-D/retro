from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional

from retro.sensors.base import BaseSensor
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class ScanScheduler(BaseSensor):
    def __init__(self):
        self._running = False
        self._on_event: Optional[Callable] = None
        self._task: Optional[asyncio.Task] = None

    def name(self) -> str:
        return "scheduler"

    def is_running(self) -> bool:
        return self._running

    async def start(self, on_event: Callable):
        self._on_event = on_event
        self._running = True
        logger.info("Scan Scheduler started")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("Scan Scheduler stopped")
