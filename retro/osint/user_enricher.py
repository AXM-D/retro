from __future__ import annotations

from retro.osint.base import BaseEnricher
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class UsernameEnricher(BaseEnricher):
    SOCIAL_PLATFORMS = [
        {"name": "GitHub", "url": "https://github.com/{}"},
        {"name": "Twitter/X", "url": "https://x.com/{}"},
        {"name": "Reddit", "url": "https://www.reddit.com/user/{}"},
        {"name": "Instagram", "url": "https://www.instagram.com/{}"},
        {"name": "Telegram", "url": "https://t.me/{}"},
        {"name": "YouTube", "url": "https://www.youtube.com/@{}"},
        {"name": "Twitch", "url": "https://www.twitch.tv/{}"},
        {"name": "TikTok", "url": "https://www.tiktok.com/@{}"},
    ]

    async def enrich(self, username: str) -> dict:
        result = {"username": username, "profiles": []}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                for platform in self.SOCIAL_PLATFORMS:
                    url = platform["url"].format(username)
                    try:
                        resp = await client.head(url, follow_redirects=True)
                        if resp.status_code < 400:
                            result["profiles"].append({
                                "platform": platform["name"],
                                "url": url,
                                "status_code": resp.status_code,
                            })
                    except Exception:
                        pass
        except ImportError:
            pass
        return result
