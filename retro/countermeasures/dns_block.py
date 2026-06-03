from __future__ import annotations

from pathlib import Path

from retro.countermeasures.base import BaseCountermeasure
from retro.utils.logger import get_logger

logger = get_logger(__name__)


class DNSBlock(BaseCountermeasure):
    def name(self) -> str:
        return "dns_block"

    async def execute(self, target: str, target_type: str = "domain", **kwargs) -> dict:
        if target_type not in ("domain", "ip"):
            return {"status": "failed", "error": "Only domain/IP supported"}
        try:
            hosts_path = Path("/etc/hosts")
            if not hosts_path.is_file():
                return {"status": "failed", "error": "/etc/hosts not found"}
            content = hosts_path.read_text()
            if target in content:
                return {"status": "already_blocked", "target": target}
            with open(hosts_path, "a") as f:
                f.write(f"\n127.0.0.1 {target}")
            logger.info(f"DNS block added for {target} in /etc/hosts")
            return {"status": "blocked", "target": target, "method": "hosts"}
        except PermissionError:
            return {"status": "failed", "error": "Permission denied (run as root)"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def dry_run(self, target: str, target_type: str = "domain") -> dict:
        return {"would_execute": "add_to_etc_hosts", "target": target}

    async def unblock(self, target: str) -> dict:
        try:
            hosts_path = Path("/etc/hosts")
            content = hosts_path.read_text()
            new_content = "\n".join(line for line in content.split("\n") if target not in line)
            hosts_path.write_text(new_content)
            return {"status": "unblocked", "target": target}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
