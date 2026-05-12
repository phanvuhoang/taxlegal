from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from backend.config import DATABASE_URL, DBVNTAX_DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, pool_pre_ping=False, pool_size=10, max_overflow=20, pool_recycle=3600)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Read-only connection to dbvntax (existing tax law database)
dbvntax_engine = create_async_engine(
    DBVNTAX_DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10
)
DbvntaxSession = async_sessionmaker(dbvntax_engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_dbvntax_db() -> AsyncSession:
    async with DbvntaxSession() as session:
        yield session
