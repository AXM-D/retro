from fastapi import APIRouter
from retro.core.config import config

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
async def get_settings():
    return {
        "version": "0.1.0",
        "debug": config.debug,
        "host": config.retro.host,
        "port": config.retro.port,
        "auto_block": config.protection.auto_block,
        "desktop_notifications": config.alerting.desktop_notifications,
        "sound_alarm": config.alerting.sound_alarm,
        "sensors": {name: {"enabled": sc.enabled, "port": getattr(sc, "port", None)} for name, sc in config.sensors.items()},
        "llm": {"provider": config.llm.provider, "model": config.llm.model},
    }
