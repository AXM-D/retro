from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, Callable, Optional

from retro.sensors.base import BaseSensor
from retro.utils.logger import get_logger

logger = get_logger(__name__)

AUTH_LOG_PATTERNS = [
    re.compile(r"Failed password for (\w+) from (\S+) port (\d+)"),
    re.compile(r"Failed password for invalid user (\w+) from (\S+) port (\d+)"),
    re.compile(r"Accepted password for (\w+) from (\S+) port (\d+)"),
    re.compile(r"Connection closed by authenticating user (\w+) (\S+) port (\d+)"),
]

NGINX_LOG_PATTERN = re.compile(
    r'(\S+) - - \[.*?\] "(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH) (\S+).*?" (\d+) (\d+) ".*?" "(.*?)"'
)


class LogImporter(BaseSensor):
    def __init__(self):
        self._running = False
        self._on_event: Optional[Callable] = None
        self._tasks: list[asyncio.Task] = []

    def name(self) -> str:
        return "log_importer"

    def is_running(self) -> bool:
        return self._running

    async def start(self, on_event: Callable):
        self._on_event = on_event
        self._running = True
        log_paths = [
            Path("/var/log/auth.log"),
            Path("/var/log/secure"),
            Path("/var/log/nginx/access.log"),
            Path("/var/log/apache2/access.log"),
            Path("/var/log/syslog"),
        ]
        for path in log_paths:
            if path.exists():
                self._tasks.append(asyncio.create_task(self._tail_log(path)))
                logger.info(f"Log importer watching: {path}")
        if not self._tasks:
            logger.warning("No log files found to import")

    async def _tail_log(self, path: Path):
        try:
            with open(path, "r") as f:
                f.seek(0, 2)
                while self._running:
                    line = f.readline()
                    if not line:
                        await asyncio.sleep(0.5)
                        continue
                    await self._parse_line(line.strip())
        except Exception as e:
            logger.warning(f"Log tail error for {path}: {e}")

    async def _parse_line(self, line: str):
        for pattern in AUTH_LOG_PATTERNS:
            m = pattern.search(line)
            if m:
                groups = m.groups()
                if len(groups) >= 3:
                    username = groups[0]
                    ip = groups[1]
                    port = groups[2]
                    event_type = "ssh_failed" if "Failed" in line else "ssh_accepted" if "Accepted" in line else "ssh_closed"
                    if self._on_event:
                        await self._on_event(
                            "log_importer", event_type, ip,
                            username=username, source_port=int(port),
                            raw_log=line[:500], protocol="ssh",
                        )
                    return

        m = NGINX_LOG_PATTERN.search(line)
        if m:
            ip = m.group(1)
            method = m.group(2)
            path = m.group(3)
            ua = m.group(6) if m.lastindex == 6 else ""
            if self._on_event:
                await self._on_event(
                    "log_importer", "http_access", ip,
                    method=method, path=path, user_agent=ua,
                    raw_log=line[:500], protocol="http",
                )

    async def stop(self):
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Log importer stopped")
