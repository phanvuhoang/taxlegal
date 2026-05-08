# TaxLegal AI — v4 Architecture

An internal AI platform for tax advisory work with configurable multi-agent workflows, DB-first legal retrieval, and durable workflow execution.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI API Layer                          │
│  /api/cases  /api/workflows  /api/bots  /api/skills  /api/health│
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────────┐
         │               │                   │
┌────────▼───────┐  ┌────▼────────┐  ┌──────▼──────────┐
│  LangGraph     │  │  Temporal   │  │  Retrieval      │
│  Orchestrator  │  │  Worker     │  │  Service        │
│  (state graph) │  │  (durable)  │  │  (DB-first)     │
└────────────────┘  └─────────────┘  └──────────────────┘
         │                                   │
         └────────────────┬──────────────────┘
                          │
         ┌────────────────┼───────────────────┐
         │                │                   │
┌────────▼───────┐  ┌─────▼──────┐  ┌────────▼───────┐
│  PostgreSQL     │  │   Redis    │  │  Temporal DB   │
│  (taxlegal      │  │  (cache/   │  │  (workflow      │
│   schema)       │  │   queue)   │  │   history)      │
└─────────────────┘  └────────────┘  └────────────────┘
```

## DB-First Retrieval Rule

**CRITICAL**: The system enforces strict DB-first retrieval:

1. Always query `taxlegal.law_documents_v2` + `dbvntax` first
2. Only if both return 0 results → fallback to Perplexity web search
3. If coverage is missing → return `"insufficient source coverage"` (never fabricate)
4. Every AI prompt gets `DB_FIRST_SYSTEM_ADDENDUM` injected
5. All retrieval is logged to `taxlegal.retrieval_queries`

## Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI 0.115+ |
| Workflow | LangGraph 0.2+ |
| Durable execution | Temporal (scaffolded) |
| Database | PostgreSQL (taxlegal schema) |
| Cache/Queue | Redis 7 |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Frontend | React + TypeScript + Vite + Tailwind |

## Quick Start (Local Docker Compose)

### 1. Prerequisites
- Docker + Docker Compose
- PostgreSQL (external or local) with `taxlegal` database
- Copy `.env.example` to `.env` and fill in your values

```bash
cp .env.example .env
# Edit .env with your DB credentials, API keys, etc.
```

### 2. Run the app (minimal — app + Redis only)
```bash
docker compose up -d
```

This starts:
- `taxlegal` — main app on port 8010
- `redis` — Redis cache on port 6379

### 3. Run with Temporal worker
```bash
docker compose --profile worker up -d
```

### 4. Run with full Temporal cluster (optional)
```bash
# Set TEMPORAL_POSTGRES_PWD in .env first
docker compose --profile temporal --profile worker up -d
# Temporal UI available at http://localhost:8088
```

### 5. Initialize the database
On first run, the app auto-creates all tables via `init_schema.sql`.
For Alembic-managed migrations:
```bash
DATABASE_URL=postgresql+asyncpg://... alembic upgrade head
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Main App | 8010 | FastAPI + React frontend |
| Redis | 6379 | Cache/queue (internal) |
| Temporal | 7233 | Workflow server (optional) |
| Temporal UI | 8088 | Workflow monitoring (optional) |

## API Endpoints

### Cases
```
POST   /api/cases                        Create case
GET    /api/cases                        List cases
GET    /api/cases/{id}                   Case detail
POST   /api/cases/{id}/start             Start workflow
GET    /api/cases/{id}/state             Workflow state
GET    /api/cases/{id}/events            Event timeline
GET    /api/cases/{id}/versions          Version history
POST   /api/cases/{id}/human-approval    Submit approval
GET    /api/cases/{id}/final             Final output
POST   /api/cases/{id}/attachments       Upload file
```

### Workflows
```
POST   /api/workflows                    Create workflow definition
PATCH  /api/workflows/{id}               Update workflow
GET    /api/workflows                    List workflows
GET    /api/workflows/{id}               Workflow detail
POST   /api/workflows/{id}/validate      Validate graph
POST   /api/workflows/{id}/nodes         Add node
POST   /api/workflows/{id}/edges         Add edge
DELETE /api/workflows/{id}/nodes/{nid}   Remove node
```

### Bots
```
POST   /api/bots                         Create bot
PATCH  /api/bots/{id}                    Update bot
GET    /api/bots                         List bots
GET    /api/bots/{id}                    Bot detail
POST   /api/bots/{id}/skills             Assign skill
DELETE /api/bots/{id}/skills/{skill_id}  Unassign skill
GET    /api/bots/{id}/preview-prompt     Preview assembled prompt
```

### Skills
```
GET    /api/skills                       List skills
POST   /api/skills                       Create skill
PATCH  /api/skills/{id}                  Update skill
DELETE /api/skills/{id}                  Delete skill
GET    /api/skills/{id}/versions         Version history
POST   /api/skills/{id}/versions         Create new version
POST   /api/skills/{id}/assign           Assign to bot
DELETE /api/skills/{id}/assign/{bot_id}  Unassign from bot
GET    /api/skills/search                Search skills
```

### Health
```
GET    /api/health                       Basic health
GET    /api/health/detailed              Full dependency check
```

## Workflow Engine

The workflow is a LangGraph state machine:

```
intake → [missing_facts?] → clarification → intake (max 2x)
       ↓ (facts OK)
   research → draft → sa_review → [approved?] → partner_review
                              ↓ (revision)         ↓
                            research            [risk>7?]
                                               human_gate
                                                   ↓
                                               delivery → audit
```

### LangGraph nodes:
1. `node_intake` — extract facts, classify case, detect missing info
2. `node_clarification` — handle missing facts (max 2 iterations)
3. `node_research` — DB-first retrieval + JA research all chunks
4. `node_draft` — assemble final advisory with retrieved sources
5. `node_sa_review` — technical review, approve or request revision
6. `node_partner_review` — strategic review, compute risk score
7. `node_human_gate` — pause for human approval when risk_score > 7
8. `node_delivery` — finalize output, compute quality score
9. `node_audit` — immutable case version snapshot

## Bot Roles

| Bot | Role | Responsibility |
|-----|------|----------------|
| intaker-bot | `intake` | Extract facts, classify, detect missing info |
| junior-bot | `ja` | Retrieve sources, draft advisory, cite everything |
| senior-bot | `sa` | Technical review, verify citations, approve/revise |
| partner-bot | `partner` | Risk assessment, client readiness, human escalation |

## Skill System

Skills are editable, versioned, and dynamically assembled into bot prompts:

- Each skill has: name, version, content, tags, applicable_bots
- Skills are assigned to bots via `bot_skill_assignments`
- Bot prompt = `base_system_prompt` + `## SKILLS ACTIVATED` section
- Edit skills in Admin → Skills; version history preserved
- Bots pick up skill changes immediately (no restart needed)

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

Test coverage:
- `test_retrieval.py` — DB-first policy, anti-fabrication guard
- `test_workflow.py` — state machine transitions
- `test_skills.py` — CRUD, versioning, assignment
- `test_workflow_validation.py` — graph validation
- `test_api_integration.py` — API integration

## Environment Variables

See `.env.example` for full list. Key variables:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/taxlegal
DBVNTAX_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/postgres
REDIS_URL=redis://localhost:6379/0
TEMPORAL_HOST=localhost:7233    # optional
SECRET_KEY=your-32-char-secret
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
```

## Data Models

New in v4 (all in `taxlegal` schema, UUID PKs):

| Table | Purpose |
|-------|---------|
| `cases` | Client advisory requests |
| `case_events` | Immutable audit timeline |
| `case_versions` | Snapshots at key milestones |
| `workflow_definitions` | Graph-based workflow templates |
| `workflow_nodes` | Individual workflow nodes |
| `workflow_edges` | Node transitions with conditions |
| `workflow_runs` | Active/completed workflow executions |
| `agent_runs` | Per-node agent execution records |
| `skill_versions` | Version history for skills |
| `bot_skill_assignments` | Bot ↔ skill mapping |
| `draft_opinions` | Advisory drafts with citations |
| `review_decisions` | SA/partner review outcomes |
| `human_approvals` | Human approval requests/decisions |
| `citations` | Source citations with trust levels |
| `retrieval_queries` | DB/web retrieval audit log |
| `approval_policies` | When to require human approval |
| `task_states` | Durable state (Redis fallback) |

## Production Deployment (Coolify)

The app is deployed via Coolify on VPS using Dockerfile mode.
Main app URL: `https://taxlegal.gpt4vn.com`

Required Coolify env vars: see `.env.example` + add `REDIS_URL` pointing to Redis instance.

For Temporal: either use an external Temporal Cloud instance, or deploy the docker-compose temporal profile separately.

## What's New in v4

Compared to v3:
- **LangGraph orchestrator** — state machine replaces hardcoded 7-step pipeline
- **DB-first retrieval** — enforced by `RetrievalService`, anti-fabrication guards
- **Temporal worker** — durable execution scaffold (ready to connect to Temporal server)
- **17 new data models** — full audit trail, versioning, citations
- **New REST API** — `/api/cases`, `/api/workflows`, `/api/bots` with graph validation
- **Skill versioning** — version history, rollback, dynamic assignment
- **Alembic migrations** — proper schema management
- **Tests** — 30+ unit/integration tests
- **Redis** — added to Docker Compose for cache/queue
- **Frontend** — Cases list/detail, Workflow Editor pages added

## What Remains (Future Work)

- Full visual drag-drop workflow builder (current: JSON editor)
- Full Temporal cluster deployment on VPS (current: scaffolded)
- pgvector semantic search integration (current: full-text only)
- Real-time SSE for workflow progress (current: polling)
- Multi-user approval workflows
- Email notifications on human approval requests
