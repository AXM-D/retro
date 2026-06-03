from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional

from retro.core.config import config
from retro.sensors.base import BaseSensor
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class HTTPHoneypot(BaseSensor):
    def __init__(self):
        self._server: Optional[asyncio.Server] = None
        self._running = False
        self._on_event: Optional[Callable] = None
        self._cfg = config.sensors.get("http_honeypot", {})

    def name(self) -> str:
        return "http_honeypot"

    def is_running(self) -> bool:
        return self._running

    async def start(self, on_event: Callable):
        self._on_event = on_event
        port = getattr(self._cfg, "port", 8080)
        server_header = getattr(self._cfg, "server_header", "Apache/2.4.57 (Ubuntu)")

        async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            peername = writer.get_extra_info("peername")
            ip = peername[0] if peername else "unknown"
            port_remote = peername[1] if peername else 0

            try:
                data = await asyncio.wait_for(reader.read(4096), timeout=10)
                raw = data.decode("utf-8", errors="ignore") if data else ""
                path = "/"
                user_agent = ""
                method = "GET"
                headers = {}
                body = ""

                for line in raw.split("\r\n"):
                    if line.startswith(("GET ", "POST ", "PUT ", "DELETE ", "HEAD ", "OPTIONS ", "PATCH ")):
                        parts = line.split(" ")
                        method = parts[0]
                        path = parts[1] if len(parts) > 1 else "/"
                    elif line.lower().startswith("user-agent:"):
                        user_agent = line.split(":", 1)[1].strip()
                    elif ":" in line:
                        k, v = line.split(":", 1)
                        headers[k.strip().lower()] = v.strip()

                parts = raw.split("\r\n\r\n", 1)
                if len(parts) > 1:
                    body = parts[1][:500]

                await self._on_event(
                    "http_honeypot", "http_request", ip,
                    source_port=port_remote, dest_port=port,
                    method=method, path=path,
                    user_agent=user_agent, headers=headers,
                    body=body, protocol="http",
                )

                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Server: {server_header}\r\n"
                    f"Content-Type: text/html\r\n"
                    f"Content-Length: 129\r\n"
                    f"Connection: close\r\n"
                    f"\r\n"
                    f"<html><body><h1>Welcome</h1><p>This site is under construction.</p></body></html>"
                )
                writer.write(response.encode())
                await writer.drain()
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                logger.warning(f"HTTP handler error: {e}")
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass

        self._server = await asyncio.start_server(handle_client, host="0.0.0.0", port=port)
        self._running = True
        logger.info(f"HTTP Honeypot listening on port {port}")

    async def stop(self):
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("HTTP Honeypot stopped")
