import os
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://legaldb_user:password@10.0.1.11:5432/taxlegal"
)
DBVNTAX_DATABASE_URL = os.getenv(
    "DBVNTAX_DATABASE_URL",
    "postgresql+asyncpg://legaldb_user:password@10.0.1.11:5432/postgres"
)

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-32-char-secret-key-here!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "168"))

# ── App ───────────────────────────────────────────────────────────────────────
APP_PORT = int(os.getenv("APP_PORT", "8000"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "vuhoang04@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123456")

# ── AI Providers ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL1 = os.getenv("OPENROUTER_MODEL1", "")
OPENROUTER_MODEL2 = os.getenv("OPENROUTER_MODEL2", "")
OPENROUTER_MODEL3 = os.getenv("OPENROUTER_MODEL3", "")
OPENROUTER_MODEL4 = os.getenv("OPENROUTER_MODEL4", "")

# ── Perplexity (web search) ───────────────────────────────────────────────────
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
PERPLEXITY_SEARCH_MODEL = os.getenv("PERPLEXITY_SEARCH_MODEL", "sonar")

# ── Model registry ────────────────────────────────────────────────────────────
def get_available_models() -> list[dict]:
    models = []
    if ANTHROPIC_API_KEY:
        models += [
            {"id": "claude-opus-4-5", "label": "Claude Opus 4.5", "provider": "anthropic"},
            {"id": "claude-sonnet-4-5", "label": "Claude Sonnet 4.5", "provider": "anthropic"},
            {"id": "claude-haiku-4-5", "label": "Claude Haiku 4.5", "provider": "anthropic"},
        ]
    if OPENAI_API_KEY:
        models += [
            {"id": "gpt-4o", "label": "GPT-4o", "provider": "openai"},
            {"id": "gpt-4o-mini", "label": "GPT-4o Mini", "provider": "openai"},
            {"id": "o3-mini", "label": "o3-mini", "provider": "openai"},
        ]
    if DEEPSEEK_API_KEY:
        models.append({"id": DEEPSEEK_MODEL, "label": f"DeepSeek ({DEEPSEEK_MODEL})", "provider": "deepseek"})
    for i, m in enumerate([OPENROUTER_MODEL1, OPENROUTER_MODEL2, OPENROUTER_MODEL3, OPENROUTER_MODEL4], 1):
        if m:
            models.append({"id": m, "label": f"OpenRouter Model {i}: {m}", "provider": "openrouter"})
    return models

# Default models per agent (can be overridden via DB settings)
DEFAULT_AGENT_MODELS = {
    "intake": DEEPSEEK_MODEL if DEEPSEEK_API_KEY else "gpt-4o",
    "partner": "claude-sonnet-4-5" if ANTHROPIC_API_KEY else "gpt-4o",
    "sa": "claude-sonnet-4-5" if ANTHROPIC_API_KEY else "gpt-4o",
    "ja": "claude-opus-4-5" if ANTHROPIC_API_KEY else "gpt-4o",
}

PRIMARY_COLOR = "#028a39"
