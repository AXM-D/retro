from __future__ import annotations

from retro.utils.logger import get_logger

logger = get_logger(__name__)


async def send_notification(title: str, message: str, urgency: str = "normal"):
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message[:256],
            app_name="RETRO",
            timeout=5,
        )
    except ImportError:
        import asyncio
        proc = await asyncio.create_subprocess_exec(
            "notify-send", title, message[:256],
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
    except Exception as e:
        logger.debug(f"Desktop notification failed: {e}")
