from __future__ import annotations

import asyncio
import platform

from retro.utils.logger import get_logger

logger = get_logger(__name__)


async def play_alarm(sound_file: str | None = None):
    system = platform.system().lower()
    try:
        if system == "linux":
            proc = await asyncio.create_subprocess_exec(
                "paplay", sound_file or "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
        elif system == "darwin":
            proc = await asyncio.create_subprocess_exec("afplay", "/System/Library/Sounds/Ping.aiff")
            await proc.wait()
    except Exception as e:
        logger.warning(f"Sound alarm failed: {e}")
