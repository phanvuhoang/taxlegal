"""
LegalAI startup: ensure 'legalai' database exists and init schema.
"""
import asyncpg
import logging
from sqlalchemy import text
from .database import legalai_engine, LegalAIBase
from . import models  # noqa: ensure models are registered with LegalAIBase

logger = logging.getLogger(__name__)

PG_BASE_URL = "postgresql://legaldb_user:PbSV8bfxQdta4ljBsDVtZEe74yjMG6l7uW3dSczT8Iaajm9MKX07wHqyf0xBTTMF@i11456c94loppyu9vzmgyb44:5432/postgres"


async def ensure_legalai_database():
    """Create legalai database if not exists."""
    try:
        conn = await asyncpg.connect(PG_BASE_URL)
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname='legalai'")
        if not exists:
            await conn.execute("CREATE DATABASE legalai OWNER legaldb_user")
            logger.info("Created database 'legalai'")
        else:
            logger.info("Database 'legalai' already exists")
        await conn.close()
    except Exception as e:
        logger.error(f"Error ensuring legalai database: {e}")
        raise


async def init_legalai_schema():
    """Create tables, extensions, and indexes."""
    async with legalai_engine.begin() as conn:
        # Enable pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

        # Create all ORM-defined tables
        await conn.run_sync(LegalAIBase.metadata.create_all)

        # Vector similarity index
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_law_chunks_embedding
            ON law_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)
        """))

        # Full-text search index on TSV column
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_law_chunks_tsv
            ON law_chunks USING GIN (tsv)
        """))

        # GIN index for array domain filtering
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_law_documents_domains
            ON law_documents USING GIN (domains)
        """))

        # TSV auto-update trigger function
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_law_chunk_tsv()
            RETURNS trigger AS $$
            BEGIN
              NEW.tsv := to_tsvector(
                'simple',
                coalesce(NEW.content,'') || ' '
                || coalesce(NEW.title,'') || ' '
                || coalesce(NEW.parent_context,'')
              );
              RETURN NEW;
            END
            $$ LANGUAGE plpgsql
        """))

        # asyncpg does not support multiple statements in one execute() call
        # — split DROP and CREATE into separate calls
        await conn.execute(text(
            "DROP TRIGGER IF EXISTS law_chunks_tsv_trigger ON law_chunks"
        ))
        await conn.execute(text("""
            CREATE TRIGGER law_chunks_tsv_trigger
            BEFORE INSERT OR UPDATE ON law_chunks
            FOR EACH ROW EXECUTE FUNCTION update_law_chunk_tsv()
        """))

        logger.info("LegalAI schema initialized")


async def run_legalai_startup():
    """Top-level startup coroutine called from main lifespan."""
    await ensure_legalai_database()
    await init_legalai_schema()
