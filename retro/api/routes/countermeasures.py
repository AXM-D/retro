from fastapi import APIRouter, HTTPException
from retro.api.schemas import CountermeasureRequest
from retro.countermeasures.firewall_block import FirewallBlock
from retro.countermeasures.abuse_report import AbuseReport
from retro.countermeasures.dns_block import DNSBlock
from retro.countermeasures.threat_feed import ThreatFeedGenerator
from retro.countermeasures.takedown_assist import TakedownAssist
from retro.storage.connection import get_session_factory
from retro.storage.models import CountermeasureModel
from retro.storage.repository import Repository
from retro.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/countermeasures", tags=["countermeasures"])

_COUNTERMEASURES = {
    "firewall_block": FirewallBlock(),
    "abuse_report": AbuseReport(),
    "dns_block": DNSBlock(),
    "threat_feed": ThreatFeedGenerator(),
    "takedown_assist": TakedownAssist(),
}


@router.post("")
async def execute_countermeasure(body: CountermeasureRequest):
    cm = _COUNTERMEASURES.get(body.action)
    if not cm:
        raise HTTPException(status_code=400, detail=f"Unknown action. Available: {list(_COUNTERMEASURES.keys())}")
    result = await cm.execute(body.target, body.target_type, comment=body.comment)
    factory = get_session_factory()
    async with factory() as session:
        repo = Repository(session)
        await repo.save_countermeasure(CountermeasureModel(
            target=body.target, target_type=body.target_type,
            action=body.action, status=result.get("status", "executed"),
            result=result,
        ))
    return {"action": body.action, "target": body.target, "result": result}


@router.get("")
async def list_countermeasures():
    factory = get_session_factory()
    async with factory() as session:
        repo = Repository(session)
        cms = await repo.get_countermeasures()
        return [{"id": cm.id, "action": cm.action, "target": cm.target, "status": cm.status, "executed_at": cm.executed_at.isoformat() if cm.executed_at else ""} for cm in cms]


@router.get("/actions")
async def list_actions():
    return {"actions": list(_COUNTERMEASURES.keys())}
