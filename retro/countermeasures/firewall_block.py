from __future__ import annotations

import asyncio
import subprocess

from retro.countermeasures.base import BaseCountermeasure
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class FirewallBlock(BaseCountermeasure):
    def name(self) -> str:
        return "firewall_block"

    async def execute(self, target: str, target_type: str = "ip", **kwargs) -> dict:
        if target_type != "ip":
            return {"status": "failed", "error": "Only IP blocking supported"}
        try:
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-C", "INPUT", "-s", target, "-j", "DROP",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            rc = await proc.wait()
            if rc == 0:
                return {"status": "already_blocked", "target": target}
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-A", "INPUT", "-s", target, "-j", "DROP",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await proc.wait()
            logger.info(f"Firewall block added for {target}")
            return {"status": "blocked", "target": target}
        except FileNotFoundError:
            os_alt = await self._try_nftables(target)
            if os_alt:
                return os_alt
            return {"status": "failed", "error": "No firewall tool found (try running as root)"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def dry_run(self, target: str, target_type: str = "ip") -> dict:
        return {"would_execute": "iptables", "target": target, "action": "DROP"}

    async def unblock(self, target: str) -> dict:
        try:
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-D", "INPUT", "-s", target, "-j", "DROP",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await proc.wait()
            return {"status": "unblocked", "target": target}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _try_nftables(self, target: str) -> dict | None:
        try:
            proc = await asyncio.create_subprocess_exec(
                "nft", "add", "rule", "inet", "filter", "input", "ip", "saddr", target, "drop",
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await proc.wait()
            return {"status": "blocked", "target": target, "via": "nftables"}
        except Exception:
            return None
