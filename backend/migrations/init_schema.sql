-- TaxLegal AI — Database Initialization
-- Creates schema 'taxlegal' and all tables on the shared VPS PostgreSQL instance.
-- Run once on first deployment.

CREATE SCHEMA IF NOT EXISTS taxlegal;

-- Users
CREATE TABLE IF NOT EXISTS taxlegal.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Agent settings
CREATE TABLE IF NOT EXISTS taxlegal.agent_settings (
    id SERIAL PRIMARY KEY,
    agent_key VARCHAR(50) UNIQUE NOT NULL,
    model_id VARCHAR(200) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    temperature FLOAT DEFAULT 0.3,
    max_tokens INTEGER DEFAULT 8000,
    system_prompt_override TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by INTEGER REFERENCES taxlegal.users(id)
);

-- Matters
CREATE TABLE IF NOT EXISTS taxlegal.matters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES taxlegal.users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    client_request TEXT NOT NULL,
    practice_area VARCHAR(100) DEFAULT 'tax',
    pipeline_mode VARCHAR(20) DEFAULT 'manual',
    status VARCHAR(50) DEFAULT 'draft',
    current_step INTEGER DEFAULT 0,
    verified_facts JSONB DEFAULT '[]',
    applicable_laws JSONB DEFAULT '[]',
    completeness_matrix JSONB DEFAULT '[]',
    word_count_floor INTEGER DEFAULT 3000,
    partner_brief JSONB,
    sa_blueprint JSONB,
    final_content TEXT,
    final_content_html TEXT,
    quality_score FLOAT,
    reason_codes JSONB DEFAULT '[]',
    verification_chain_status VARCHAR(50),
    model_used_intake VARCHAR(200),
    model_used_partner VARCHAR(200),
    model_used_sa VARCHAR(200),
    model_used_ja VARCHAR(200),
    total_tokens INTEGER DEFAULT 0,
    duration_ms INTEGER,
    is_sample BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_matters_user_id ON taxlegal.matters(user_id);
CREATE INDEX IF NOT EXISTS idx_matters_status ON taxlegal.matters(status);

-- Pipeline steps
CREATE TABLE IF NOT EXISTS taxlegal.pipeline_steps (
    id SERIAL PRIMARY KEY,
    matter_id INTEGER NOT NULL REFERENCES taxlegal.matters(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    agent VARCHAR(50) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    model_used VARCHAR(200),
    provider_used VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    output_markdown TEXT,
    verified_facts JSONB DEFAULT '[]',
    legal_verification JSONB DEFAULT '[]',
    assertion_verification JSONB DEFAULT '[]',
    reason_codes_found JSONB DEFAULT '[]',
    word_count INTEGER,
    search_queries JSONB DEFAULT '[]',
    search_results_summary JSONB DEFAULT '[]',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    user_notes TEXT,
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES taxlegal.users(id),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pipeline_steps_matter_id ON taxlegal.pipeline_steps(matter_id);

-- Research chunks
CREATE TABLE IF NOT EXISTS taxlegal.research_chunks (
    id SERIAL PRIMARY KEY,
    matter_id INTEGER NOT NULL REFERENCES taxlegal.matters(id) ON DELETE CASCADE,
    chunk_number INTEGER NOT NULL,
    section_title VARCHAR(500),
    depth_level VARCHAR(20) DEFAULT 'STANDARD',
    content_markdown TEXT,
    evidence_collected JSONB DEFAULT '[]',
    practical_research JSONB DEFAULT '[]',
    legal_verification JSONB DEFAULT '[]',
    assertion_verification JSONB DEFAULT '[]',
    depth_markers JSONB DEFAULT '[]',
    depth_marker_count INTEGER DEFAULT 0,
    citations JSONB DEFAULT '[]',
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample advices
CREATE TABLE IF NOT EXISTS taxlegal.sample_advices (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    practice_area VARCHAR(100) DEFAULT 'tax',
    tags TEXT[],
    client_question TEXT,
    content_markdown TEXT NOT NULL,
    content_html TEXT,
    quality_score FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AutoTest cases
CREATE TABLE IF NOT EXISTS taxlegal.autotest_cases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    description TEXT,
    client_request TEXT NOT NULL,
    practice_area VARCHAR(100) DEFAULT 'tax',
    complexity VARCHAR(20) DEFAULT 'standard',
    expected_topics JSONB DEFAULT '[]',
    forbidden_topics JSONB DEFAULT '[]',
    scoring_criteria JSONB DEFAULT '{}',
    baseline_score FLOAT,
    baseline_locked_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AutoTest runs
CREATE TABLE IF NOT EXISTS taxlegal.autotest_runs (
    id SERIAL PRIMARY KEY,
    test_case_id INTEGER NOT NULL REFERENCES taxlegal.autotest_cases(id) ON DELETE CASCADE,
    matter_id INTEGER REFERENCES taxlegal.matters(id),
    run_by INTEGER REFERENCES taxlegal.users(id),
    score_total FLOAT,
    score_breakdown JSONB DEFAULT '{}',
    reason_codes_triggered JSONB DEFAULT '[]',
    delta_from_baseline FLOAT,
    mutation_description TEXT,
    passed BOOLEAN,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Law documents (local cache for taxlegal-specific laws)
CREATE TABLE IF NOT EXISTS taxlegal.law_documents (
    id SERIAL PRIMARY KEY,
    so_hieu VARCHAR(200),
    ten TEXT NOT NULL,
    loai VARCHAR(20),
    co_quan VARCHAR(100),
    ngay_ban_hanh VARCHAR(30),
    hieu_luc_tu VARCHAR(30),
    het_hieu_luc_tu VARCHAR(30),
    tinh_trang VARCHAR(50) DEFAULT 'con_hieu_luc',
    replaced_by VARCHAR(200),
    practice_areas TEXT[],
    content_text TEXT,
    link_tvpl TEXT,
    dbvntax_id INTEGER,
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_law_docs_so_hieu ON taxlegal.law_documents(so_hieu);

-- Seed default agent settings (will be overridden via admin UI)
INSERT INTO taxlegal.agent_settings (agent_key, model_id, provider, temperature, max_tokens)
VALUES
  ('intake',  'deepseek-chat',      'deepseek',   0.2, 8000),
  ('partner', 'claude-sonnet-4-5',  'anthropic',  0.3, 6000),
  ('sa',      'claude-sonnet-4-5',  'anthropic',  0.2, 8000),
  ('ja',      'claude-opus-4-5',    'anthropic',  0.3, 16000)
ON CONFLICT (agent_key) DO NOTHING;

-- Seed default autotest cases
INSERT INTO taxlegal.autotest_cases (name, description, client_request, practice_area, complexity,
    expected_topics, scoring_criteria)
VALUES (
  'Test đơn giản: Thuế nhà thầu nước ngoài',
  'Test case cơ bản — phải trả lời đủ 3 loại thuế: GTGT, TNDN nhà thầu, và chi phí được trừ',
  'Công ty Việt Nam trả tiền mua phần mềm từ Microsoft Ireland. Thuế nhà thầu thế nào? Chi phí có được trừ không?',
  'tax', 'simple',
  '["thuế GTGT", "thuế TNDN nhà thầu", "chi phí được trừ", "chứng từ"]',
  '{"structure": 20, "legal_accuracy": 30, "practicality": 25, "completeness": 25}'
) ON CONFLICT DO NOTHING;

-- Skills
CREATE TABLE IF NOT EXISTS taxlegal.skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    description TEXT,
    category VARCHAR(50) DEFAULT 'tax',
    tags TEXT[],
    applicable_bots TEXT[],
    content_markdown TEXT NOT NULL,
    frontmatter JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_builtin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES taxlegal.users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_skills_name ON taxlegal.skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON taxlegal.skills(category);

-- BotVariants
CREATE TABLE IF NOT EXISTS taxlegal.bot_variants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    description TEXT,
    system_prompt_base TEXT,
    skill_ids INTEGER[] DEFAULT '{}',
    model_override VARCHAR(200),
    provider_override VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_builtin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_bot_variants_slug ON taxlegal.bot_variants(slug);
CREATE INDEX IF NOT EXISTS idx_bot_variants_role ON taxlegal.bot_variants(role);

-- PipelineTemplates
CREATE TABLE IF NOT EXISTS taxlegal.pipeline_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    practice_area VARCHAR(50) DEFAULT 'tax',
    step_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pipeline_templates_slug ON taxlegal.pipeline_templates(slug);

-- Add pipeline_template_id to matters
ALTER TABLE taxlegal.matters
    ADD COLUMN IF NOT EXISTS pipeline_template_id INTEGER REFERENCES taxlegal.pipeline_templates(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS bot_variant_overrides JSONB DEFAULT '{}';
-- bot_variant_overrides: per-matter override map {step: bot_variant_slug}
