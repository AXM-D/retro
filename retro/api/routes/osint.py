from fastapi import APIRouter, HTTPException
from retro.osint.profile_builder import ProfileBuilder

router = APIRouter(prefix="/osint", tags=["osint"])
builder = ProfileBuilder()


@router.get("/{entity_type}/{value}")
async def osint_lookup(entity_type: str, value: str):
    valid_types = ["ip", "email", "domain", "hash", "username", "phone"]
    if entity_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid type. Valid: {valid_types}")
    try:
        profile = await builder.build(entity_type, value)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investigate")
async def investigate_event(event_id: str):
    from retro.core.engine import engine
    result = await engine.run_osint(event_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "completed", "investigation": result}
