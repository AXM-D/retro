from __future__ import annotations

import asyncio
import socket
from typing import Any, Callable

from retro.core.config import config
from retro.sensors.base import BaseSensor
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class SSHHoneypot(BaseSensor):
    def __init__(self):
        self._server: Optional[asyncio.Server] = None
        self._running = False
        self._on_event: Optional[Callable] = None
        self._cfg = config.sensors.get("ssh_honeypot", {})

    def name(self) -> str:
        return "ssh_honeypot"

    def is_running(self) -> bool:
        return self._running

    async def start(self, on_event: Callable):
        self._on_event = on_event
        port = getattr(self._cfg, "port", 2222)
        banner = getattr(self._cfg, "banner", "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3")
        self._banner = f"{banner}\r\n"

        async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            peername = writer.get_extra_info("peername")
            ip = peername[0] if peername else "unknown"
            port_remote = peername[1] if peername else 0
            logger.info(f"SSH connection from {ip}:{port_remote}")

            writer.write(self._banner.encode())
            await writer.drain()

            try:
                line = await asyncio.wait_for(reader.readline(), timeout=10)
                if line:
                    raw = line.decode("utf-8", errors="ignore").strip()
                    username = "unknown"
                    if raw.startswith("SSH-"):
                        username = raw
                    else:
                        try:
                            import base64
                            decoded = base64.b64decode(raw).decode("utf-8", errors="ignore")
                            if "\x00" in decoded:
                                parts = decoded.split("\x00")
                                username = parts[0] if len(parts) > 0 else raw
                        except Exception:
                            username = raw[:100]

                    await asyncio.sleep(2)
                    writer.write(b"\x00\x00\x00\x04\x0e\x00\x00\x00\x00\x00\x00\x00\x00")
                    await writer.drain()
                    await asyncio.sleep(0.5)

                    try:
                        password_line = await asyncio.wait_for(reader.readline(), timeout=5)
                        password = password_line.decode("utf-8", errors="ignore").strip()[:100]
                    except asyncio.TimeoutError:
                        password = ""

                    await self._on_event(
                        "ssh_honeypot", "ssh_attempt", ip,
                        source_port=port_remote, dest_port=port,
                        username=username, password=password,
                        protocol="ssh",
                    )
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                logger.warning(f"SSH handler error: {e}")
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass

        self._server = await asyncio.start_server(handle_client, host="0.0.0.0", port=port)
        self._running = True
        logger.info(f"SSH Honeypot listening on port {port}")

    async def stop(self):
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("SSH Honeypot stopped")
