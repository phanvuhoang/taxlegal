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


# ── Skills / BotVariants / PipelineTemplates seed ─────────────────────────────

DEFAULT_BOT_VARIANTS = [
    {
        "name": "Intake Enhancer (Default)",
        "slug": "intake-default",
        "role": "intake",
        "description": "Bot tiếp nhận và xác minh sự kiện mặc định",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot (Default)",
        "slug": "partner-default",
        "role": "partner",
        "description": "Partner Bot mặc định — lập brief và review chiến lược",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "SA Bot (Default)",
        "slug": "sa-default",
        "role": "sa",
        "description": "SA Bot mặc định — blueprint và adversarial review",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot (Default)",
        "slug": "ja-default",
        "role": "ja",
        "description": "JA Bot mặc định — 5-phase research pipeline",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Advisory",
        "slug": "ja-advisory",
        "role": "ja",
        "description": "JA Bot chuyên viết advisory memo tư vấn thuế — dùng skill advisory-memo + tax-strategy",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Compliance",
        "slug": "ja-compliance",
        "role": "ja",
        "description": "JA Bot chuyên về compliance check — kiểm tra tuân thủ quy định thuế",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — CIT Specialist",
        "slug": "partner-cit",
        "role": "partner",
        "description": "Partner Bot chuyên về Thuế TNDN (CIT) — dùng skill vietnam-cit",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — VAT Specialist",
        "slug": "partner-vat",
        "role": "partner",
        "description": "Partner Bot chuyên về Thuế GTGT (VAT) — dùng skill vietnam-vat",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — FCT Specialist",
        "slug": "partner-fct",
        "role": "partner",
        "description": "Partner Bot chuyên về Thuế Nhà thầu nước ngoài (FCT) — dùng skill vietnam-fct",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — Transfer Pricing",
        "slug": "partner-tp",
        "role": "partner",
        "description": "Partner Bot chuyên về Chuyển giá (TP) — dùng skill vietnam-transfer-pricing",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — FCT Research",
        "slug": "ja-fct",
        "role": "ja",
        "description": "JA Bot chuyên nghiên cứu FCT — dùng skill vietnam-fct + vietnam-dta",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Transfer Pricing",
        "slug": "ja-tp",
        "role": "ja",
        "description": "JA Bot chuyên về Transfer Pricing — dùng skill vietnam-transfer-pricing",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Tax Admin & Audit",
        "slug": "ja-tax-admin",
        "role": "ja",
        "description": "JA Bot chuyên về quy trình thanh/kiểm tra thuế — dùng skill vietnam-tax-admin",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "SA Bot — Compliance Review",
        "slug": "sa-compliance",
        "role": "sa",
        "description": "SA Bot chuyên về compliance review — kiểm tra tuân thủ đa loại thuế",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
]

DEFAULT_PIPELINE_TEMPLATES = [
    {
        "name": "Standard Default",
        "slug": "standard-default",
        "description": "Pipeline mặc định — tất cả bước dùng bot mặc định",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-default", "label": "Partner Brief"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-default", "label": "JA Research"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-default", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-default", "label": "Partner P3 Finalize"},
        },
        "is_default": True,
        "is_active": True,
    },
    {
        "name": "CIT Advisory Deep",
        "slug": "cit-advisory-deep",
        "description": "Pipeline chuyên về tư vấn Thuế TNDN — dùng Partner-CIT và JA-Advisory",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-cit", "label": "Partner Brief (CIT Specialist)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-advisory", "label": "JA Research (Advisory)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-cit", "label": "Partner P2 Review (CIT)"},
            "7": {"bot_variant_slug": "partner-cit", "label": "Partner P3 Finalize (CIT)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "VAT Compliance Check",
        "slug": "vat-compliance-check",
        "description": "Pipeline kiểm tra tuân thủ Thuế GTGT — dùng Partner-VAT và JA-Compliance",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-vat", "label": "Partner Brief (VAT Specialist)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-compliance", "label": "JA Compliance Check"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-vat", "label": "Partner P2 Review (VAT)"},
            "7": {"bot_variant_slug": "partner-vat", "label": "Partner P3 Finalize (VAT)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "CIT Compliance Check",
        "slug": "cit-compliance-check",
        "description": "Pipeline kiểm tra tuân thủ Thuế TNDN — provisional/annual CIT return review",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-cit", "label": "Partner Brief (CIT)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-compliance", "label": "JA Compliance Check"},
            "5": {"bot_variant_slug": "sa-compliance", "label": "SA Compliance Review"},
            "6": {"bot_variant_slug": "partner-cit", "label": "Partner P2 Review (CIT)"},
            "7": {"bot_variant_slug": "partner-cit", "label": "Partner P3 Finalize (CIT)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "VAT Advisory Deep",
        "slug": "vat-advisory-deep",
        "description": "Pipeline tư vấn chuyên sâu Thuế GTGT — dùng Partner-VAT và JA-Advisory",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-vat", "label": "Partner Brief (VAT Specialist)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-advisory", "label": "JA Research (Advisory)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-vat", "label": "Partner P2 Review (VAT)"},
            "7": {"bot_variant_slug": "partner-vat", "label": "Partner P3 Finalize (VAT)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "PIT Advisory Deep",
        "slug": "pit-advisory-deep",
        "description": "Pipeline tư vấn chuyên sâu Thuế TNCN — expat, stock options, multiple income sources",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-default", "label": "Partner Brief (PIT)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-advisory", "label": "JA Research (Advisory)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-default", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-default", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "PIT Compliance Check",
        "slug": "pit-compliance-check",
        "description": "Pipeline kiểm tra tuân thủ Thuế TNCN — withholding, annual finalization",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-default", "label": "Partner Brief (PIT)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-compliance", "label": "JA Compliance Check"},
            "5": {"bot_variant_slug": "sa-compliance", "label": "SA Compliance Review"},
            "6": {"bot_variant_slug": "partner-default", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-default", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "FCT Advisory",
        "slug": "fct-advisory",
        "description": "Pipeline tư vấn Thuế Nhà thầu nước ngoài — FCT declaration/direct method analysis",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-fct", "label": "Partner Brief (FCT Specialist)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-fct", "label": "JA FCT Research"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-fct", "label": "Partner P2 Review (FCT)"},
            "7": {"bot_variant_slug": "partner-fct", "label": "Partner P3 Finalize (FCT)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "Transfer Pricing Review",
        "slug": "transfer-pricing-review",
        "description": "Pipeline rà soát chuyển giá — arm's length analysis, Decree 132/2020 compliance",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-tp", "label": "Partner Brief (TP Specialist)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-tp", "label": "JA Transfer Pricing Research"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-tp", "label": "Partner P2 Review (TP)"},
            "7": {"bot_variant_slug": "partner-tp", "label": "Partner P3 Finalize (TP)"},
        },
        "is_default": False,
        "is_active": True,
    },
]

# Maps bot slug → skill names to link after seeding
BOT_SKILL_LINKS = {
    "ja-advisory": ["advisory-memo", "tax-strategy"],
    "ja-compliance": ["tax-compliance"],
    "partner-cit": ["vietnam-cit"],
    "partner-vat": ["vietnam-vat"],
    "partner-fct": ["vietnam-fct"],
    "partner-tp": ["vietnam-transfer-pricing"],
    "ja-fct": ["vietnam-fct", "vietnam-dta"],
    "ja-tp": ["vietnam-transfer-pricing"],
    "ja-tax-admin": ["vietnam-tax-admin"],
}


async def seed_skills_and_bots():
    """
    1. Scan /skills/*.md files and upsert into taxlegal.skills
    2. Seed default BotVariants
    3. Seed default PipelineTemplates
    4. Link skill_ids to bots based on BOT_SKILL_LINKS
    """
    import json
    import re
    from pathlib import Path

    # Fix existing is_builtin records
    async with AsyncSessionLocal() as db:
        await db.execute(text("UPDATE taxlegal.skills SET is_builtin = FALSE WHERE is_builtin = TRUE"))
        await db.execute(text("UPDATE taxlegal.bot_variants SET is_builtin = FALSE WHERE is_builtin = TRUE"))
        await db.commit()
        logger.info("Cleared is_builtin flags on skills and bot_variants.")

    try:
        import yaml  # PyYAML
        HAS_YAML = True
    except ImportError:
        HAS_YAML = False
        logger.warning("PyYAML not installed — skill frontmatter will be stored as empty dict")

    skills_dir = Path(__file__).parent.parent / "skills"

    async with AsyncSessionLocal() as db:
        # ── 1. Seed skills from .md files ──────────────────────────────────────
        seeded_skill_names = []
        if skills_dir.exists():
            for md_file in sorted(skills_dir.glob("*.md")):
                try:
                    raw = md_file.read_text(encoding="utf-8")
                    # Parse YAML frontmatter
                    frontmatter = {}
                    body = raw
                    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', raw, re.DOTALL)
                    if fm_match and HAS_YAML:
                        try:
                            frontmatter = yaml.safe_load(fm_match.group(1)) or {}
                        except Exception:
                            frontmatter = {}
                        body = raw[fm_match.end():]
                    elif fm_match:
                        body = raw[fm_match.end():]

                    skill_name = frontmatter.get("name") or md_file.stem
                    version = str(frontmatter.get("version", "1.0.0"))
                    description = frontmatter.get("description", "")
                    category = frontmatter.get("category", "tax")
                    tags = frontmatter.get("tags") or []
                    applicable_bots = frontmatter.get("bots") or []

                    await db.execute(text("""
                        INSERT INTO taxlegal.skills
                            (name, version, description, category, tags, applicable_bots,
                             content_markdown, frontmatter, is_active, is_builtin)
                        VALUES
                            (:name, :version, :description, :category, :tags, :applicable_bots,
                             :content_markdown, :frontmatter, TRUE, FALSE)
                        ON CONFLICT (name) DO UPDATE SET
                            version = EXCLUDED.version,
                            description = EXCLUDED.description,
                            category = EXCLUDED.category,
                            tags = EXCLUDED.tags,
                            applicable_bots = EXCLUDED.applicable_bots,
                            content_markdown = EXCLUDED.content_markdown,
                            frontmatter = EXCLUDED.frontmatter,
                            updated_at = NOW()
                    """), {
                        "name": skill_name,
                        "version": version,
                        "description": description,
                        "category": category,
                        "tags": tags,
                        "applicable_bots": applicable_bots,
                        "content_markdown": body.strip(),
                        "frontmatter": json.dumps(frontmatter),
                    })
                    seeded_skill_names.append(skill_name)
                    logger.info(f"Seeded skill: {skill_name}")
                except Exception as e:
                    logger.warning(f"Failed to seed skill {md_file}: {e}")
        else:
            logger.info("No /skills/ directory found — skipping skill file seed")

        await db.commit()

        # ── 2. Seed BotVariants ────────────────────────────────────────────────
        for bv in DEFAULT_BOT_VARIANTS:
            await db.execute(text("""
                INSERT INTO taxlegal.bot_variants
                    (name, slug, role, description, system_prompt_base, skill_ids,
                     is_builtin, is_active)
                VALUES
                    (:name, :slug, :role, :description, :system_prompt_base, :skill_ids,
                     :is_builtin, :is_active)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    role = EXCLUDED.role,
                    description = EXCLUDED.description,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """), {
                "name": bv["name"],
                "slug": bv["slug"],
                "role": bv["role"],
                "description": bv["description"],
                "system_prompt_base": bv.get("system_prompt_base"),
                "skill_ids": bv.get("skill_ids", []),
                "is_builtin": bv.get("is_builtin", False),
                "is_active": bv.get("is_active", True),
            })
        await db.commit()
        logger.info("BotVariants seeded.")

        # ── 3. Seed PipelineTemplates ──────────────────────────────────────────
        for pt in DEFAULT_PIPELINE_TEMPLATES:
            await db.execute(text("""
                INSERT INTO taxlegal.pipeline_templates
                    (name, slug, description, practice_area, step_config, is_default, is_active)
                VALUES
                    (:name, :slug, :description, :practice_area, :step_config, :is_default, :is_active)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    practice_area = EXCLUDED.practice_area,
                    step_config = EXCLUDED.step_config,
                    is_default = EXCLUDED.is_default,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """), {
                "name": pt["name"],
                "slug": pt["slug"],
                "description": pt["description"],
                "practice_area": pt["practice_area"],
                "step_config": json.dumps(pt["step_config"]),
                "is_default": pt["is_default"],
                "is_active": pt["is_active"],
            })
        await db.commit()
        logger.info("PipelineTemplates seeded.")

        # ── 4. Link skill_ids to bots ─────────────────────────────────────────
        for bot_slug, skill_names in BOT_SKILL_LINKS.items():
            if not skill_names:
                continue
            # Get skill IDs
            placeholders = ", ".join([f":s{i}" for i in range(len(skill_names))])
            params = {f"s{i}": name for i, name in enumerate(skill_names)}
            result = await db.execute(
                text(f"SELECT id FROM taxlegal.skills WHERE name IN ({placeholders})"),
                params,
            )
            skill_ids = [row[0] for row in result.fetchall()]
            if skill_ids:
                await db.execute(text("""
                    UPDATE taxlegal.bot_variants
                    SET skill_ids = :skill_ids, updated_at = NOW()
                    WHERE slug = :slug
                """), {"skill_ids": skill_ids, "slug": bot_slug})
                logger.info(f"Linked skills {skill_ids} to bot variant '{bot_slug}'")

        await db.commit()
        logger.info("Skill–BotVariant links updated.")

    # ── 5. Seed default workflow definition ──────────────────────────────────
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("""
                INSERT INTO taxlegal.workflow_definitions
                    (id, name, slug, description, version, is_active, is_default, practice_area, entry_node, graph_definition)
                VALUES
                    (gen_random_uuid(), 'Tax Advisory Standard', 'tax-advisory-standard',
                     'Standard 7-step tax advisory pipeline', 1, TRUE, TRUE, 'tax', 'intake',
                     '{"nodes": ["intake","research","draft","sa_review","partner_review","human_gate","delivery","audit"],
                       "edges": [
                         {"from": "intake", "to": "research", "condition": "default"},
                         {"from": "research", "to": "draft"},
                         {"from": "draft", "to": "sa_review"},
                         {"from": "sa_review", "to": "partner_review", "condition": "approved"},
                         {"from": "sa_review", "to": "research", "condition": "revision_required"},
                         {"from": "partner_review", "to": "delivery", "condition": "approved"},
                         {"from": "partner_review", "to": "human_gate", "condition": "human_approval_required"},
                         {"from": "human_gate", "to": "delivery", "condition": "approved"},
                         {"from": "delivery", "to": "audit"}
                       ]
                     }'::jsonb)
                ON CONFLICT (slug) DO NOTHING
            """))
            await db.commit()
            logger.info("Default workflow definition seeded.")
        except Exception as e:
            logger.warning(f"Could not seed default workflow definition (table may not exist yet): {e}")

    logger.info("seed_skills_and_bots() complete.")
