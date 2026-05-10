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
    """Run migrations/init_schema.sql to create schema and tables.
    Each statement runs in its own transaction so one failure
    does not abort the rest (safe for idempotent CREATE IF NOT EXISTS).
    """
    sql_path = Path(__file__).parent / "migrations" / "init_schema.sql"
    sql = sql_path.read_text()
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    ok = 0
    skipped = 0
    for stmt in statements:
        try:
            async with engine.begin() as conn:   # each stmt = own transaction
                await conn.execute(text(stmt))
            ok += 1
        except Exception as e:
            skipped += 1
            logger.warning(f"SQL stmt skipped (likely already exists): {str(e)[:120]}")
    logger.info(f"Schema init: {ok} OK, {skipped} skipped.")
    logger.info("Schema initialization complete.")

    # Explicit column migrations — ensure v4 columns exist on existing DBs
    # These run on every startup (ADD COLUMN IF NOT EXISTS = idempotent)
    _col_migrations = [
        # taxlegal.skills — v4 columns
        "ALTER TABLE taxlegal.skills ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1",
        "ALTER TABLE taxlegal.skills ADD COLUMN IF NOT EXISTS parent_skill_id INTEGER REFERENCES taxlegal.skills(id)",
        "ALTER TABLE taxlegal.skills ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES taxlegal.users(id)",
        # taxlegal.bot_variants — v4 columns
        "ALTER TABLE taxlegal.bot_variants ADD COLUMN IF NOT EXISTS model_override VARCHAR(100)",
        "ALTER TABLE taxlegal.bot_variants ADD COLUMN IF NOT EXISTS provider_override VARCHAR(50)",
        "ALTER TABLE taxlegal.bot_variants ADD COLUMN IF NOT EXISTS node_type VARCHAR(50) DEFAULT 'agent'",
        # taxlegal.pipeline_templates — v4 columns
        "ALTER TABLE taxlegal.pipeline_templates ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE",
        # taxlegal.matters — v4 columns
        "ALTER TABLE taxlegal.matters ADD COLUMN IF NOT EXISTS output_language VARCHAR(10) DEFAULT 'vi'",
        "ALTER TABLE taxlegal.matters ADD COLUMN IF NOT EXISTS pipeline_template_id INTEGER",
        "ALTER TABLE taxlegal.matters ADD COLUMN IF NOT EXISTS assigned_bot_variant_id INTEGER",
    ]
    async with engine.begin() as conn:
        for migration in _col_migrations:
            try:
                await conn.execute(text(migration))
            except Exception as e:
                logger.warning(f"Column migration warning (may already exist): {e}")
    logger.info("Column migrations applied.")

    # Run additional migration files (002, 003, ...)
    migrations_dir = Path(__file__).parent / "migrations"
    for migration_file in sorted(migrations_dir.glob("[0-9][0-9][0-9]_*.sql")):
        try:
            extra_sql = migration_file.read_text()
            extra_stmts = [s.strip() for s in extra_sql.split(";") if s.strip() and not s.strip().startswith("--")]
            ok2 = 0
            skip2 = 0
            for stmt in extra_stmts:
                try:
                    async with engine.begin() as conn:
                        await conn.execute(text(stmt))
                    ok2 += 1
                except Exception as e:
                    skip2 += 1
                    logger.warning(f"[{migration_file.name}] stmt skipped: {str(e)[:120]}")
            logger.info(f"Migration {migration_file.name}: {ok2} OK, {skip2} skipped.")
        except Exception as e:
            logger.warning(f"Migration file {migration_file.name} failed to load: {e}")


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
    # ── JA Specialists: PIT / VAT / CIT / SST / IntlTax ──────────────────────
    {
        "name": "JA Bot — PIT Specialist",
        "slug": "ja-pit",
        "role": "ja",
        "description": "JA Bot chuyên về Thuế TNCN — expats, RSU/equity, benefits-in-kind, phân bổ xuyên biên giới",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — VAT Specialist",
        "slug": "ja-vat",
        "role": "ja",
        "description": "JA Bot chuyên về Thuế GTGT — khấu trừ, hoàn thuế, hóa đơn, VAT xuyên biên giới",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — CIT Specialist",
        "slug": "ja-cit",
        "role": "ja",
        "description": "JA Bot chuyên về Thuế TNDN — ưu đãi, khấu hao, chuyển lỗ, phân bổ chi phí",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — SST/TTĐB Specialist",
        "slug": "ja-sst",
        "role": "ja",
        "description": "JA Bot chuyên về Thuế Tiêu thụ Đặc biệt — phân loại hàng hóa, biểu thuế suất, khấu trừ TTĐB",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — International Tax",
        "slug": "ja-intl-tax",
        "role": "ja",
        "description": "JA Bot chuyên về thuế quốc tế — PE risk, FTC, BEPS/Pillar Two, DTA, indirect transfer, beneficial ownership",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    # ── SA Specialists ────────────────────────────────────────────────────────
    {
        "name": "SA Bot — Advisory Review",
        "slug": "sa-advisory",
        "role": "sa",
        "description": "SA Bot chuyên về advisory review — kiểm tra IRAC, adversarial review, phê duyệt memo tư vấn",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "SA Bot — CIT Specialist",
        "slug": "sa-cit",
        "role": "sa",
        "description": "SA Bot chuyên về CIT — review kỹ thuật thuế TNDN, ưu đãi, phân bổ chi phí",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "SA Bot — VAT Specialist",
        "slug": "sa-vat",
        "role": "sa",
        "description": "SA Bot chuyên về VAT — review kỹ thuật thuế GTGT, khấu trừ, hoàn thuế",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    # ── Partner Specialists: PIT / SST / IntlTax ──────────────────────────────
    {
        "name": "Partner Bot — PIT Specialist",
        "slug": "partner-pit",
        "role": "partner",
        "description": "Partner Bot chuyên về Thuế TNCN — lập brief, review chiến lược cho expat, equity, cá nhân kinh doanh",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — SST/TTĐB Specialist",
        "slug": "partner-sst",
        "role": "partner",
        "description": "Partner Bot chuyên về Thuế TTĐB — lập brief, review chiến lược cho nhà SX và NK hàng chịu TTĐB",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — International Tax",
        "slug": "partner-intl-tax",
        "role": "partner",
        "description": "Partner Bot chuyên về thuế quốc tế — cross-border, DTA, Pillar Two, PE analysis",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    # ── PIT 2026 Specialists ──────────────────────────────────────────────────
    {
        "name": "JA Bot — PIT 2026 Core",
        "slug": "ja-pit-2026",
        "role": "ja",
        "description": "JA Bot chuyên PIT 2026 (Luật 109/2025) — biểu thuế 5 bậc, giảm trừ mới, ngưỡng HKD 1 tỷ",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — PIT Finalization",
        "slug": "ja-pit-finalization",
        "role": "ja",
        "description": "JA Bot quyết toán TNCN — SOP eTax Mobile, điều kiện ủy quyền, deadline, tình huống phức tạp",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — PIT Freelancer & KOL",
        "slug": "ja-pit-freelancer",
        "role": "ja",
        "description": "JA Bot thuế TNCN freelancer, KOL, content creator — decision tree, tỷ lệ thuế theo ngành",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — PIT Expat & Non-Resident",
        "slug": "ja-pit-expat",
        "role": "ja",
        "description": "JA Bot PIT người nước ngoài — 183-day rule, gross-up, DTA credit, equity xuyên biên giới",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — PIT 2026 Specialist",
        "slug": "partner-pit-2026",
        "role": "partner",
        "description": "Partner Bot PIT 2026 — lập brief, review chiến lược với biểu thuế và giảm trừ mới nhất",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    # ── VAT Specialists ───────────────────────────────────────────────────────
    {
        "name": "JA Bot — VAT Input Deductibility",
        "slug": "ja-vat-input",
        "role": "ja",
        "description": "JA Bot khấu trừ thuế GTGT đầu vào — điều kiện, HĐĐT, FCT, phân bổ doanh thu hỗn hợp",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — VAT Invoice & Supplier",
        "slug": "ja-vat-invoice",
        "role": "ja",
        "description": "JA Bot hóa đơn GTGT — kiểm tra tính hợp lệ HĐĐT, supplier pattern library, hóa đơn ảo",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — VAT Export & Zero Rate",
        "slug": "ja-vat-export",
        "role": "ja",
        "description": "JA Bot GTGT xuất khẩu — điều kiện 0%, hoàn thuế, dịch vụ xuyên biên giới",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    # ── Customs Specialists ───────────────────────────────────────────────────
    {
        "name": "JA Bot — Customs Import Duty",
        "slug": "ja-customs-import",
        "role": "ja",
        "description": "JA Bot thuế nhập khẩu — HS Code, CIF, FTA thuế suất, GTGT NK, miễn giảm",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Customs HS Classification",
        "slug": "ja-customs-hs",
        "role": "ja",
        "description": "JA Bot phân loại HS Code — GRI rules, nhóm hàng phổ biến, advance ruling, rủi ro sai phân loại",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Customs Origin & FTA",
        "slug": "ja-customs-origin",
        "role": "ja",
        "description": "JA Bot xuất xứ hàng hóa — WO/CTC/RVC, C/O types, cộng gộp, gian lận xuất xứ",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "JA Bot — Customs Procedures",
        "slug": "ja-customs-procedures",
        "role": "ja",
        "description": "JA Bot thủ tục hải quan — TNTX, gia công, SXXK, kho ngoại quan, EPZ, kiểm tra, phạt vi phạm",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "Partner Bot — Customs Specialist",
        "slug": "partner-customs",
        "role": "partner",
        "description": "Partner Bot hải quan — tư vấn chiến lược, tối ưu FTA, AEO, kiểm toán hải quan",
        "system_prompt_base": None,
        "skill_ids": [],
        "is_builtin": False,
        "is_active": True,
    },
    {
        "name": "SA Bot — Customs Compliance",
        "slug": "sa-customs",
        "role": "sa",
        "description": "SA Bot hải quan — review kỹ thuật compliance, PCA prep, tranh chấp trị giá",
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
    # ── SST / TTĐB Pipelines ────────────────────────────────────────────────
    {
        "name": "SST Advisory",
        "slug": "sst-advisory",
        "description": "Pipeline tư vấn Thuế TTĐB — phân loại hàng hóa, thiết kế cấu trúc thuế tối ưu",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-sst", "label": "Partner Brief (SST Specialist)"},
            "3": {"bot_variant_slug": "sa-advisory", "label": "SA Blueprint (Advisory)"},
            "4": {"bot_variant_slug": "ja-sst", "label": "JA SST Research"},
            "5": {"bot_variant_slug": "sa-advisory", "label": "SA Review (Advisory)"},
            "6": {"bot_variant_slug": "partner-sst", "label": "Partner P2 Review (SST)"},
            "7": {"bot_variant_slug": "partner-sst", "label": "Partner P3 Finalize (SST)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "SST Compliance Check",
        "slug": "sst-compliance-check",
        "description": "Pipeline kiểm tra tuân thủ Thuế TTĐB — khai báo, nộp thuế, khấu trừ TTĐB",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-sst", "label": "Partner Brief (SST)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-sst", "label": "JA SST Compliance Check"},
            "5": {"bot_variant_slug": "sa-compliance", "label": "SA Compliance Review"},
            "6": {"bot_variant_slug": "partner-sst", "label": "Partner P2 Review (SST)"},
            "7": {"bot_variant_slug": "partner-sst", "label": "Partner P3 Finalize (SST)"},
        },
        "is_default": False,
        "is_active": True,
    },
    # ── International Tax Pipelines ─────────────────────────────────────────
    {
        "name": "International Tax Advisory",
        "slug": "intl-tax-advisory",
        "description": "Pipeline tư vấn thuế quốc tế — PE risk, FTC, Pillar Two, cross-border payments",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-intl-tax", "label": "Partner Brief (Intl Tax)"},
            "3": {"bot_variant_slug": "sa-advisory", "label": "SA Blueprint (Advisory)"},
            "4": {"bot_variant_slug": "ja-intl-tax", "label": "JA International Tax Research"},
            "5": {"bot_variant_slug": "sa-advisory", "label": "SA Review (Advisory)"},
            "6": {"bot_variant_slug": "partner-intl-tax", "label": "Partner P2 Review (Intl Tax)"},
            "7": {"bot_variant_slug": "partner-intl-tax", "label": "Partner P3 Finalize (Intl Tax)"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "DTA Analysis",
        "slug": "dta-analysis",
        "description": "Pipeline phân tích Hiệp định tránh đánh thuế hai lần (DTA) — beneficial ownership, WHT reduction, treaty shopping",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-intl-tax", "label": "Partner Brief (DTA Specialist)"},
            "3": {"bot_variant_slug": "sa-advisory", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-intl-tax", "label": "JA DTA Research"},
            "5": {"bot_variant_slug": "sa-advisory", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-intl-tax", "label": "Partner P2 Review (DTA)"},
            "7": {"bot_variant_slug": "partner-intl-tax", "label": "Partner P3 Finalize (DTA)"},
        },
        "is_default": False,
        "is_active": True,
    },
    # ── PIT Specialist Pipelines ───────────────────────────────────────────────
    {
        "name": "PIT Advisory — Expat & Equity",
        "slug": "pit-advisory-expat",
        "description": "Pipeline tư vấn TNCN chuyên sâu cho expat, RSU/stock options, benefits-in-kind",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-pit", "label": "Partner Brief (PIT Specialist)"},
            "3": {"bot_variant_slug": "sa-advisory", "label": "SA Blueprint (Advisory)"},
            "4": {"bot_variant_slug": "ja-pit", "label": "JA PIT Research (Expat)"},
            "5": {"bot_variant_slug": "sa-advisory", "label": "SA Review (Advisory)"},
            "6": {"bot_variant_slug": "partner-pit", "label": "Partner P2 Review (PIT)"},
            "7": {"bot_variant_slug": "partner-pit", "label": "Partner P3 Finalize (PIT)"},
        },
        "is_default": False,
        "is_active": True,
    },
    # ── Generic Work-Type Pipelines ───────────────────────────────────────────
    {
        "name": "Compliance Review Standard",
        "slug": "compliance-review-standard",
        "description": "Pipeline kiểm tra tuân thủ chuẩn — dùng cho mọi loại thuế, quy trình data request → reconciliation → filing gate",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-default", "label": "Partner Brief"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-compliance", "label": "JA Compliance Check"},
            "5": {"bot_variant_slug": "sa-compliance", "label": "SA Compliance Review"},
            "6": {"bot_variant_slug": "partner-default", "label": "Partner P2 Sign-Off"},
            "7": {"bot_variant_slug": "partner-default", "label": "Partner P3 Delivery"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "Advisory Memo Standard",
        "slug": "advisory-memo-standard",
        "description": "Pipeline viết advisory memo chuẩn — dùng cho mọi loại thuế, quy trình IRAC → SA review → Partner phê duyệt",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
            "2": {"bot_variant_slug": "partner-default", "label": "Partner Brief"},
            "3": {"bot_variant_slug": "sa-advisory", "label": "SA Blueprint (Advisory)"},
            "4": {"bot_variant_slug": "ja-advisory", "label": "JA Research (Advisory)"},
            "5": {"bot_variant_slug": "sa-advisory", "label": "SA Review (Advisory)"},
            "6": {"bot_variant_slug": "partner-default", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-default", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
]

# ── NEW PIPELINES (PIT 2026 + VAT Advanced + Customs) ──────────────────────
DEFAULT_PIPELINE_TEMPLATES_V2 = [
    {
        "name": "PIT 2026 Advisory",
        "slug": "pit-2026-advisory",
        "description": "Pipeline tư vấn TNCN 2026 — Luật 109/2025, biểu thuế 5 bậc, giảm trừ mới",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-pit-2026", "label": "Partner Brief (PIT 2026)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-pit-2026", "label": "JA Research (PIT 2026)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-pit-2026", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-pit-2026", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "PIT Finalization (Quyết Toán)",
        "slug": "pit-finalization",
        "description": "Pipeline quyết toán thuế TNCN năm — cố vấn SOP eTax Mobile và mẫu biểu",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-pit-2026", "label": "Partner Brief (Quyết Toán)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-pit-finalization", "label": "JA Research (Finalization)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-pit-2026", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-pit-2026", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "PIT Freelancer & KOL Advisory",
        "slug": "pit-freelancer-advisory",
        "description": "Pipeline tư vấn thuế TNCN freelancer, KOL, content creator",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-pit-2026", "label": "Partner Brief (Freelancer)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-pit-freelancer", "label": "JA Research (Freelancer/KOL)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-pit-2026", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-pit-2026", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "PIT Expat & Non-Resident",
        "slug": "pit-expat-nonresident",
        "description": "Pipeline thuế TNCN người nước ngoài — 183-day rule, gross-up, DTA",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-pit", "label": "Partner Brief (PIT Expat)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-pit-expat", "label": "JA Research (Expat/Non-Resident)"},
            "5": {"bot_variant_slug": "sa-default", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-pit", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-pit", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "VAT Input & Invoice Review",
        "slug": "vat-input-invoice-review",
        "description": "Pipeline kiểm tra khấu trừ GTGT đầu vào và hóa đơn điện tử",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-vat", "label": "Partner Brief (VAT)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-vat-input", "label": "JA Research (Input Deductibility)"},
            "5": {"bot_variant_slug": "sa-vat", "label": "SA Review (VAT)"},
            "6": {"bot_variant_slug": "partner-vat", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-vat", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "VAT Export Zero Rate",
        "slug": "vat-export-zero-rate",
        "description": "Pipeline tư vấn GTGT xuất khẩu 0% — điều kiện, bằng chứng, hoàn thuế",
        "practice_area": "tax",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-vat", "label": "Partner Brief (VAT Export)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-vat-export", "label": "JA Research (Export 0%)"},
            "5": {"bot_variant_slug": "sa-vat", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-vat", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-vat", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "Customs Import Advisory",
        "slug": "customs-import-advisory",
        "description": "Pipeline tư vấn nhập khẩu — thuế NK, HS Code, FTA, miễn giảm",
        "practice_area": "customs",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-customs", "label": "Partner Brief (Customs)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-customs-import", "label": "JA Research (Import Duty)"},
            "5": {"bot_variant_slug": "sa-customs", "label": "SA Review (Customs)"},
            "6": {"bot_variant_slug": "partner-customs", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-customs", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "Customs HS Classification",
        "slug": "customs-hs-classification",
        "description": "Pipeline phân loại HS Code — GRI rules, advance ruling, chứng minh phân loại",
        "practice_area": "customs",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-customs", "label": "Partner Brief (HS)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-customs-hs", "label": "JA Research (HS Classification)"},
            "5": {"bot_variant_slug": "sa-customs", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-customs", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-customs", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "Customs Origin & FTA Optimization",
        "slug": "customs-origin-fta",
        "description": "Pipeline xuất xứ hàng hóa và tối ưu thuế FTA",
        "practice_area": "customs",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-customs", "label": "Partner Brief (Origin/FTA)"},
            "3": {"bot_variant_slug": "sa-default", "label": "SA Blueprint"},
            "4": {"bot_variant_slug": "ja-customs-origin", "label": "JA Research (Origin/FTA)"},
            "5": {"bot_variant_slug": "sa-customs", "label": "SA Review"},
            "6": {"bot_variant_slug": "partner-customs", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-customs", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
    {
        "name": "Customs Compliance Review",
        "slug": "customs-compliance-review",
        "description": "Pipeline kiểm toán tuân thủ hải quan — PCA prep, AEO, tranh chấp trị giá",
        "practice_area": "customs",
        "step_config": {
            "1": {"bot_variant_slug": "intake-default", "label": "Intake"},
            "2": {"bot_variant_slug": "partner-customs", "label": "Partner Brief (Compliance)"},
            "3": {"bot_variant_slug": "sa-customs", "label": "SA Blueprint (Customs)"},
            "4": {"bot_variant_slug": "ja-customs-procedures", "label": "JA Research (Procedures)"},
            "5": {"bot_variant_slug": "sa-customs", "label": "SA Review (Compliance)"},
            "6": {"bot_variant_slug": "partner-customs", "label": "Partner P2 Review"},
            "7": {"bot_variant_slug": "partner-customs", "label": "Partner P3 Finalize"},
        },
        "is_default": False,
        "is_active": True,
    },
]

# Merge V2 pipelines into DEFAULT_PIPELINE_TEMPLATES
DEFAULT_PIPELINE_TEMPLATES.extend(DEFAULT_PIPELINE_TEMPLATES_V2)


# Maps bot slug → skill names to link after seeding
BOT_SKILL_LINKS = {
    # ── Existing bots ───────────────────────────────────────────────────────────────
    "ja-advisory": ["advisory-memo", "tax-strategy", "advisory-workflow", "source-hierarchy"],
    "ja-compliance": ["tax-compliance", "compliance-checklist", "source-hierarchy"],
    "partner-cit": ["vietnam-cit"],
    "partner-vat": ["vietnam-vat"],
    "partner-fct": ["vietnam-fct"],
    "partner-tp": ["vietnam-transfer-pricing"],
    "ja-fct": ["vietnam-fct", "vietnam-dta", "source-hierarchy"],
    "ja-tp": ["vietnam-transfer-pricing", "source-hierarchy"],
    "ja-tax-admin": ["vietnam-tax-admin"],
    "sa-compliance": ["compliance-checklist", "tax-compliance"],
    "sa-advisory": ["advisory-workflow", "advisory-memo"],
    # ── New JA Specialists ──────────────────────────────────────────────────
    "ja-pit": ["vietnam-pit", "pit-advanced", "source-hierarchy"],
    "ja-vat": ["vietnam-vat", "vietnam-invoices", "source-hierarchy"],
    "ja-cit": ["vietnam-cit", "source-hierarchy"],
    "ja-sst": ["vietnam-sst-advanced", "source-hierarchy"],
    "ja-intl-tax": ["vietnam-intl-tax", "vietnam-dta", "source-hierarchy"],
    # ── New SA Specialists ───────────────────────────────────────────────────
    "sa-cit": ["vietnam-cit", "tax-compliance"],
    "sa-vat": ["vietnam-vat", "tax-compliance"],
    # ── New Partner Specialists ─────────────────────────────────────────────
    "partner-pit": ["vietnam-pit", "pit-advanced"],
    "partner-sst": ["vietnam-sst-advanced"],
    "partner-intl-tax": ["vietnam-intl-tax", "vietnam-dta"],
    # ── PIT 2026 Specialists ─────────────────────────────────────────────────
    "ja-pit-2026": ["pit-2026-core", "pit-bhxh-bhtn", "source-hierarchy"],
    "ja-pit-finalization": ["pit-finalization", "pit-deadline-tracker", "source-hierarchy"],
    "ja-pit-freelancer": ["pit-freelancer-kol", "pit-2026-core", "source-hierarchy"],
    "ja-pit-expat": ["pit-expat-nonresident", "pit-advanced", "source-hierarchy"],
    "partner-pit-2026": ["pit-2026-core", "pit-finalization", "pit-freelancer-kol", "pit-expat-nonresident"],
    # ── VAT Specialists ──────────────────────────────────────────────────────
    "ja-vat-input": ["vat-input-deductibility", "vat-invoice-validity", "vietnam-vat", "source-hierarchy"],
    "ja-vat-invoice": ["vat-invoice-validity", "vietnam-invoices", "source-hierarchy"],
    "ja-vat-export": ["vat-export-zero-rate", "vat-return-review", "source-hierarchy"],
    # ── Customs Specialists ──────────────────────────────────────────────────
    "ja-customs-import": ["vietnam-customs-core", "vietnam-import-duty", "vietnam-hs-classification", "source-hierarchy"],
    "ja-customs-hs": ["vietnam-hs-classification", "vietnam-customs-core", "source-hierarchy"],
    "ja-customs-origin": ["vietnam-origin-fta", "vietnam-customs-core", "source-hierarchy"],
    "ja-customs-procedures": ["vietnam-customs-procedures", "vietnam-customs-compliance", "source-hierarchy"],
    "partner-customs": ["vietnam-customs-core", "vietnam-import-duty", "vietnam-customs-advisory", "vietnam-origin-fta"],
    "sa-customs": ["vietnam-customs-compliance", "vietnam-customs-valuation", "vietnam-customs-procedures"],
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
                    applicable_bots = frontmatter.get("applicable_bots") or frontmatter.get("bots") or []

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
            # asyncpg cannot bind a JSON string as INTEGER[] via parameter.
            # Embed the array literal directly in SQL to avoid type ambiguity.
            skill_ids_list = bv.get("skill_ids", []) or []
            if skill_ids_list:
                _arr = "ARRAY[" + ",".join(str(i) for i in skill_ids_list) + "]::INTEGER[]"
            else:
                _arr = "ARRAY[]::INTEGER[]"
            await db.execute(text(f"""
                INSERT INTO taxlegal.bot_variants
                    (name, slug, role, description, system_prompt_base, skill_ids,
                     is_builtin, is_active)
                VALUES
                    (:name, :slug, :role, :description, :system_prompt_base, {_arr},
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
                # asyncpg cannot bind Python list as INTEGER[] parameter.
                # Embed the array literal directly in SQL.
                _arr = "ARRAY[" + ",".join(str(i) for i in skill_ids) + "]::INTEGER[]"
                await db.execute(text(f"""
                    UPDATE taxlegal.bot_variants
                    SET skill_ids = {_arr}, updated_at = NOW()
                    WHERE slug = :slug
                """), {"slug": bot_slug})
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
