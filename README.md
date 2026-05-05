# TaxLegal AI

**AI-powered Tax & Legal Advisory Platform** — based on EZLAW-AI V15.1 architecture.

## Overview

TaxLegal AI orchestrates 4 specialized AI agents through a 7-step pipeline to produce professional-grade tax and legal advisory documents for the Vietnamese market.

### Pipeline Steps
| Step | Agent | Role |
|------|-------|------|
| 1 | **Intake Enhancer** | Fact verification (Tier 1), legal currency check, completeness matrix |
| 2 | **Partner P1** | Strategic brief, scope confirmation, DEEP/STANDARD classification |
| 3 | **SA Blueprint** | Document architecture, chunk division, dedup map |
| 4 | **JA Research** | Phase A→B1→B2→B2.5→C per chunk, depth markers |
| 5 | **SA Adversarial Review** | Independent spot-check, devil's advocate, R-code detection |
| 6 | **Partner P2** | Verification chain audit (Tier 5), strategic quality review |
| 7 | **Partner P3** | Finalize, executive summary, client-ready document |

### Key Quality Features
- **5-Tier Verification Chain** — each tier independently verifies the tier before it
- **17 Quality Mechanisms** (Legal Currency Check, Completeness Matrix, Word Count Floor, Devil's Advocate, etc.)
- **18 Reason Codes** (R01–R18) with CRITICAL / MODERATE severity
- **Depth Markers**: `[PRACTICAL]`, `[PITFALL]`, `[INDUSTRY]`, `[COUNTER]`, `[ANTICIPATE]`
- **AutoTest Module** — baseline locking, mutation loop, anti-inflation

## Tech Stack

- **Backend**: FastAPI (Python 3.12, async), SQLAlchemy, PostgreSQL
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **AI Providers**: Anthropic / OpenAI / DeepSeek / OpenRouter
- **Web Search**: Perplexity Sonar API (fact & legal verification)
- **Deploy**: Docker → Coolify VPS

## Database Setup

TaxLegal uses a **schema `taxlegal`** within the existing shared PostgreSQL instance on VPS.
It also connects read-only to **`dbvntax`** (existing tax law database from taxconsult project).

Schema is auto-created on first startup via `migrations/init_schema.sql`.

## Deployment (Coolify)

1. Add GitHub repo `phanvuhoang/taxlegal`
2. Set build pack: **Dockerfile**
3. Configure env vars (see `.env.example`)
4. Set port mapping: `8010:8000` (or your preferred port)
5. Deploy — schema and admin user auto-created on first run

### Required Env Vars
```
DATABASE_URL=postgresql+asyncpg://...
DBVNTAX_DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
ANTHROPIC_API_KEY=...  (or OPENAI_API_KEY / DEEPSEEK_API_KEY)
PERPLEXITY_API_KEY=...
```

## Default Admin
- Email: `vuhoang04@gmail.com`
- Password: `Admin@123456`

## Law Database Strategy

The app uses a **3-layer approach** for legal references:
1. **dbvntax** (existing): Rich tax law database with full text, auto-connected read-only
2. **taxlegal.law_documents**: Local cache for non-tax laws, manually added or synced
3. **Web search (Perplexity)**: Real-time verification of law currency for every citation
