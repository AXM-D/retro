from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from typing import Any, Callable, Optional

from retro.core.config import config
from retro.sensors.base import BaseSensor
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class PortScanDetector(BaseSensor):
    def __init__(self):
        self._running = False
        self._on_event: Optional[Callable] = None
        self._cfg = config.sensors.get("port_scan_detector", {})
        self._connections: dict[str, list[float]] = defaultdict(list)
        self._cleanup_task: Optional[asyncio.Task] = None

    def name(self) -> str:
        return "port_scan_detector"

    def is_running(self) -> bool:
        return self._running

    async def start(self, on_event: Callable):
        self._on_event = on_event
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Port Scan Detector started")

    async def _cleanup_loop(self):
        window = getattr(self._cfg, "window_seconds", 60)
        while self._running:
            await asyncio.sleep(window)
            now = time.monotonic()
            cutoff = now - window
            for ip in list(self._connections.keys()):
                self._connections[ip] = [t for t in self._connections[ip] if t > cutoff]
                if not self._connections[ip]:
                    del self._connections[ip]

    async def record_connection(self, ip: str):
        if not self._running:
            return
        now = time.monotonic()
        threshold = getattr(self._cfg, "threshold", 10)
        window = getattr(self._cfg, "window_seconds", 60)
        cutoff = now - window
        self._connections[ip] = [t for t in self._connections[ip] if t > cutoff]
        self._connections[ip].append(now)
        if len(self._connections[ip]) >= threshold and self._on_event:
            await self._on_event(
                "port_scan_detector", "port_scan", ip,
                connection_count=len(self._connections[ip]),
                window_seconds=window,
                protocol="tcp",
            )
            self._connections[ip] = []

    async def stop(self):
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Port Scan Detector stopped")
