from __future__ import annotations

from retro.core.config import config
from retro.utils.logger import get_logger

logger = get_logger(__name__)

_webhooks: dict[str, str] = {}


def register_webhook(name: str, url: str):
    _webhooks[name] = url


async def send_webhook(message: str, webhook_name: str | None = None):
    urls = [url for name, url in _webhooks.items() if webhook_name is None or name == webhook_name]
    if not urls:
        return
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            for url in urls:
                try:
                    if "discord" in url:
                        await client.post(url, json={"content": message[:2000]})
                    elif "slack" in url:
                        await client.post(url, json={"text": message[:2000]})
                    elif "telegram" in url or "t.me" in url:
                        await client.post(url, json={"chat_id": "", "text": message[:2000]})
                    else:
                        await client.post(url, json={"message": message[:2000]})
                except Exception as e:
                    logger.warning(f"Webhook {url[:30]}... failed: {e}")
    except ImportError:
        logger.warning("httpx not installed for webhooks")
