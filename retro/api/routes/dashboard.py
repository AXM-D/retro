from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from retro.api.schemas import DashboardResponse, AttackEventResponse, AttackerResponse
from retro.core.engine import engine
from retro.storage.connection import get_session_factory
from retro.storage.repository import Repository

router = APIRouter(tags=["dashboard"])


async def get_repo() -> Repository:
    factory = get_session_factory()
    async with factory() as session:
        yield Repository(session)


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(repo: Repository = Depends(get_repo)):
    return await repo.get_dashboard()


@router.get("/events", response_model=list[AttackEventResponse])
async def list_events(limit: int = 100):
    events = await engine.get_events(limit)
    return [AttackEventResponse(**e.to_dict()) for e in events]


@router.get("/attackers", response_model=list[AttackerResponse])
async def list_attackers():
    attackers = await engine.get_attackers()
    return [AttackerResponse(**a.to_dict()) for a in attackers]


@router.get("/attackers/{ip}", response_model=AttackerResponse)
async def get_attacker(ip: str):
    a = await engine.get_attacker(ip)
    if not a:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Attacker not found")
    return AttackerResponse(**a.to_dict())
