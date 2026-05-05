"""
Startup tasks: create database (if needed), schema, seed admin user, seed agent settings.
Called from main.py lifespan.
"""
import asyncio
import logging
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from backend.database import engine, AsyncSessionLocal
from backend.models import Base, User, AgentSetting
from backend.auth import hash_password
from backend.config import ADMIN_EMAIL, ADMIN_PASSWORD, DEFAULT_AGENT_MODELS, DATABASE_URL

logger = logging.getLogger(__name__)


async def ensure_database_exists():
    """
    Connect to 'postgres' default database and CREATE DATABASE taxlegal if it doesn't exist.
    Works even if the target database doesn't exist yet.
    """
    # Extract target db name and build connection to postgres default db
    import re
    match = re.search(r'/(\w+)$', DATABASE_URL)
    if not match:
        logger.warning("Could not parse database name from DATABASE_URL")
        return
    db_name = match.group(1)
    if db_name == 'postgres':
        return  # Already using default db

    # Build URL pointing to 'postgres' db instead
    postgres_url = DATABASE_URL[:DATABASE_URL.rfind('/')] + '/postgres'
    tmp_engine = create_async_engine(postgres_url, isolation_level='AUTOCOMMIT', pool_pre_ping=True)
    try:
        async with tmp_engine.connect() as conn:
            # Check if db exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name}
            )
            exists = result.scalar_one_or_none()
            if not exists:
                logger.info(f"Database '{db_name}' not found — creating...")
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
    except Exception as e:
        logger.error(f"Could not ensure database exists: {e}")
    finally:
        await tmp_engine.dispose()


async def run_init_sql():
    """Run migrations/init_schema.sql to create schema and tables."""
    sql_path = Path(__file__).parent / "migrations" / "init_schema.sql"
    sql = sql_path.read_text()
    async with engine.begin() as conn:
        # Execute statement by statement (split on semicolons, ignore empty)
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                logger.warning(f"SQL stmt warning (may be OK if already exists): {e}")
    logger.info("Schema initialization complete.")


async def seed_admin():
    """Create admin user if not exists."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info(f"Admin user {ADMIN_EMAIL} already exists.")
            return
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            full_name="Administrator",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        logger.info(f"Admin user {ADMIN_EMAIL} created successfully.")


async def seed_agent_settings():
    """Ensure all 4 agent settings exist in DB."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        for agent_key, model_id in DEFAULT_AGENT_MODELS.items():
            result = await db.execute(
                select(AgentSetting).where(AgentSetting.agent_key == agent_key)
            )
            existing = result.scalar_one_or_none()
            if not existing:
                # Determine provider
                if "claude" in model_id:
                    provider = "anthropic"
                elif "gpt" in model_id or "o3" in model_id:
                    provider = "openai"
                elif "deepseek" in model_id:
                    provider = "deepseek"
                else:
                    provider = "openrouter"
                setting = AgentSetting(
                    agent_key=agent_key,
                    model_id=model_id,
                    provider=provider,
                    temperature=0.2 if agent_key in ("intake", "sa") else 0.3,
                    max_tokens=16000 if agent_key == "ja" else 8000,
                )
                db.add(setting)
        await db.commit()
        logger.info("Agent settings seeded.")


async def run_startup():
    await ensure_database_exists()
    await run_init_sql()
    await seed_admin()
    await seed_agent_settings()
