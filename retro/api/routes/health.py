from fastapi import APIRouter
from retro import __version__, __app_name__
from retro.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(version=__version__, app=__app_name__)
