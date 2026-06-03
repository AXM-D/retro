from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class SensorConfig:
    enabled: bool = False
    port: int = 2222
    banner: str = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3"
    server_header: str = "Apache/2.4.57 (Ubuntu)"
    threshold: int = 10
    window_seconds: int = 60


@dataclass
class ProtectionConfig:
    auto_block: bool = False
    geo_block_enabled: bool = False
    rate_limiting_enabled: bool = False


@dataclass
class AlertingConfig:
    desktop_notifications: bool = True
    sound_alarm: bool = False


@dataclass
class LLMConfig:
    provider: str = "ollama"
    model: str = "mistral:7b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.1
    max_tokens: int = 2048


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "console"


@dataclass
class RetroAppConfig:
    host: str = "127.0.0.1"
    port: int = 8500
    data_dir: Path = Path("./data")
    max_concurrent_investigations: int = 5


@dataclass
class AppConfig:
    debug: bool = False
    secret_key: str = "change-me"
    retro: RetroAppConfig = field(default_factory=RetroAppConfig)
    sensors: dict = field(default_factory=lambda: {
        "ssh_honeypot": SensorConfig(),
        "http_honeypot": SensorConfig(enabled=False, port=8080, server_header="Apache/2.4.57 (Ubuntu)"),
        "port_scan_detector": SensorConfig(enabled=False, threshold=10, window_seconds=60),
    })
    protection: ProtectionConfig = field(default_factory=ProtectionConfig)
    alerting: AlertingConfig = field(default_factory=AlertingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> AppConfig:
        path = Path(path)
        if not path.exists():
            return cls()
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data or {})

    @classmethod
    def from_env(cls) -> AppConfig:
        return cls(
            debug=os.getenv("RETRO_DEBUG", "false").lower() == "true",
            secret_key=os.getenv("RETRO_SECRET_KEY", "change-me"),
            retro=RetroAppConfig(
                host=os.getenv("RETRO_HOST", "127.0.0.1"),
                port=int(os.getenv("RETRO_PORT", "8500")),
                data_dir=Path(os.getenv("RETRO_DATA_DIR", "./data")),
            ),
            logging=LoggingConfig(
                level=os.getenv("RETRO_LOG_LEVEL", "INFO"),
            ),
        )

    @classmethod
    def _from_dict(cls, data: dict) -> AppConfig:
        retro_cfg = data.get("retro", {})
        sensors_cfg = data.get("sensors", {})
        prot_cfg = data.get("protection", {})
        alert_cfg = data.get("alerting", {})
        llm_cfg = data.get("llm", {})
        log_cfg = data.get("logging", {})

        sensors = {}
        for name, default in [("ssh_honeypot", SensorConfig()), ("http_honeypot", SensorConfig(enabled=False, port=8080)), ("port_scan_detector", SensorConfig(enabled=False, threshold=10, window_seconds=60))]:
            sc = sensors_cfg.get(name, {})
            sensors[name] = SensorConfig(
                enabled=sc.get("enabled", default.enabled),
                port=sc.get("port", default.port),
                banner=sc.get("banner", getattr(default, "banner", "")),
                server_header=sc.get("server_header", getattr(default, "server_header", "")),
                threshold=sc.get("threshold", getattr(default, "threshold", 10)),
                window_seconds=sc.get("window_seconds", getattr(default, "window_seconds", 60)),
            )

        return cls(
            debug=data.get("debug", False),
            secret_key=data.get("secret_key", "change-me"),
            retro=RetroAppConfig(
                host=retro_cfg.get("host", "127.0.0.1"),
                port=retro_cfg.get("port", 8500),
                data_dir=Path(retro_cfg.get("data_dir", "./data")),
                max_concurrent_investigations=retro_cfg.get("max_concurrent_investigations", 5),
            ),
            sensors=sensors,
            protection=ProtectionConfig(
                auto_block=prot_cfg.get("auto_block", False),
                geo_block_enabled=prot_cfg.get("geo_block_enabled", False),
                rate_limiting_enabled=prot_cfg.get("rate_limiting_enabled", False),
            ),
            alerting=AlertingConfig(
                desktop_notifications=alert_cfg.get("desktop_notifications", True),
                sound_alarm=alert_cfg.get("sound_alarm", False),
            ),
            llm=LLMConfig(
                provider=llm_cfg.get("provider", "ollama"),
                model=llm_cfg.get("model", "mistral:7b"),
                base_url=llm_cfg.get("base_url", "http://localhost:11434"),
                temperature=llm_cfg.get("temperature", 0.1),
                max_tokens=llm_cfg.get("max_tokens", 2048),
            ),
            logging=LoggingConfig(
                level=log_cfg.get("level", "INFO"),
                format=log_cfg.get("format", "console"),
            ),
        )


config: AppConfig = AppConfig.from_env()


def load_config(path: str | Path | None = None) -> AppConfig:
    global config
    if path:
        config = AppConfig.from_yaml(path)
    else:
        config = AppConfig.from_env()
    return config
