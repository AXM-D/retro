from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from retro.core.config import config
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class FirewallManager:
    def __init__(self):
        self._rules: dict[str, list[str]] = {"blocked": []}
        self._auto_block = config.protection.auto_block

    async def block_ip(self, ip: str, persistent: bool = True) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await proc.wait()
            if ip not in self._rules["blocked"]:
                self._rules["blocked"].append(ip)
            if persistent:
                await self._save_rules()
            logger.info(f"FirewallManager: Blocked {ip}")
            return True
        except FileNotFoundError:
            return await self._nftables_block(ip)
        except Exception as e:
            logger.warning(f"Firewall block failed for {ip}: {e}")
            return False

    async def unblock_ip(self, ip: str) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await proc.wait()
            self._rules["blocked"] = [x for x in self._rules["blocked"] if x != ip]
            await self._save_rules()
            logger.info(f"FirewallManager: Unblocked {ip}")
            return True
        except Exception as e:
            logger.warning(f"Firewall unblock failed for {ip}: {e}")
            return False

    async def is_blocked(self, ip: str) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-C", "INPUT", "-s", ip, "-j", "DROP",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            rc = await proc.wait()
            return rc == 0
        except Exception:
            return ip in self._rules["blocked"]

    async def get_blocked_ips(self) -> list[str]:
        return self._rules["blocked"].copy()

    async def _nftables_block(self, ip: str) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "nft", "add", "rule", "inet", "filter", "input", "ip", "saddr", ip, "counter", "drop",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await proc.wait()
            self._rules["blocked"].append(ip)
            return True
        except Exception:
            return False

    async def _save_rules(self):
        rules_file = Path(config.retro.data_dir) / "firewall_rules.json"
        try:
            import json
            rules_file.parent.mkdir(parents=True, exist_ok=True)
            rules_file.write_text(json.dumps(self._rules, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save firewall rules: {e}")

    async def restore_rules(self):
        rules_file = Path(config.retro.data_dir) / "firewall_rules.json"
        if rules_file.exists():
            try:
                import json
                self._rules = json.loads(rules_file.read_text())
                for ip in self._rules.get("blocked", []):
                    await self.block_ip(ip, persistent=False)
                logger.info(f"Restored {len(self._rules.get('blocked', []))} firewall rules")
            except Exception as e:
                logger.warning(f"Failed to restore firewall rules: {e}")


firewall_manager = FirewallManager()
