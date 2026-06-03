from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from retro.core.config import config
from retro.storage.models import Base

_engine = None
_sync_engine = None
_factory = None


def get_engine():
    global _engine
    if _engine is None:
        db_path = str(config.retro.data_dir / "retro.db")
        _engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=config.debug)
    return _engine


def get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        db_path = str(config.retro.data_dir / "retro.db")
        _sync_engine = create_engine(f"sqlite:///{db_path}", echo=config.debug)
    return _sync_engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _factory
    if _factory is None:
        _factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _factory


async def init_database():
    config.retro.data_dir.mkdir(parents=True, exist_ok=True)
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Base.metadata.create_all(get_sync_engine())


async def close_database():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
