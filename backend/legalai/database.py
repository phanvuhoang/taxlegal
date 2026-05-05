"""
LegalAI module — dedicated database connection to `legalai` DB.
Uses async SQLAlchemy just like the main taxlegal database.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

LEGALAI_DATABASE_URL = os.getenv(
    "LEGALAI_DATABASE_URL",
    "postgresql+asyncpg://legaldb_user:PbSV8bfxQdta4ljBsDVtZEe74yjMG6l7uW3dSczT8Iaajm9MKX07wHqyf0xBTTMF@i11456c94loppyu9vzmgyb44:5432/legalai"
)

legalai_engine = create_async_engine(
    LEGALAI_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

LegalAISession = sessionmaker(legalai_engine, class_=AsyncSession, expire_on_commit=False)
LegalAIBase = declarative_base()

async def get_legalai_db():
    async with LegalAISession() as session:
        try:
            yield session
        finally:
            await session.close()
