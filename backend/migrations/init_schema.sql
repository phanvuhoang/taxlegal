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
    output_language VARCHAR(2) DEFAULT 'vi',
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

ALTER TABLE taxlegal.matters ADD COLUMN IF NOT EXISTS output_language VARCHAR(2) DEFAULT 'vi';

-- Writing Module tables
CREATE TABLE IF NOT EXISTS taxlegal.writing_jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content_type VARCHAR(50) DEFAULT 'analysis',
    topic TEXT NOT NULL,
    context TEXT,
    output_language VARCHAR(2) DEFAULT 'vi',
    bot_variant_id INTEGER,
    skill_ids INTEGER[] DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'draft',
    word_count_target INTEGER DEFAULT 2000,
    sections JSONB DEFAULT '[]',
    final_content TEXT,
    docx_path VARCHAR(500),
    gamma_url VARCHAR(500),
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS taxlegal.writing_sections (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES taxlegal.writing_jobs(id) ON DELETE CASCADE,
    section_order INTEGER NOT NULL,
    section_title VARCHAR(300),
    prompt TEXT,
    content TEXT,
    token_count INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS taxlegal.priority_docs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    doc_type VARCHAR(100),
    source_url VARCHAR(1000),
    content TEXT NOT NULL,
    embedding vector(1536),
    priority_level INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS taxlegal.sample_writings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content_type VARCHAR(50),
    language VARCHAR(2) DEFAULT 'vi',
    content TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Law Documents (Văn bản Luật) — full text HTML storage
-- ============================================================
CREATE TABLE IF NOT EXISTS taxlegal.law_documents_v2 (
    id SERIAL PRIMARY KEY,
    title VARCHAR(1000) NOT NULL,
    doc_number VARCHAR(200),          -- e.g. "103/2014/TT-BTC"
    doc_type VARCHAR(100),            -- luat | nghi_dinh | thong_tu | van_ban_hop_nhat | cong_van | hiep_dinh
    issuer VARCHAR(300),              -- e.g. "Bộ Tài chính"
    issued_date DATE,
    effective_date DATE,
    content_html TEXT,                -- full HTML content
    content_text TEXT,                -- stripped plain text for search/embedding
    source_url VARCHAR(1000),
    tags TEXT[] DEFAULT '{}',
    is_priority BOOLEAN DEFAULT FALSE, -- marks as priority/anchor doc
    embedding vector(1536),
    ai_tagged BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    imported_from VARCHAR(50),        -- 'crawler' | 'upload' | 'dbvntax' | 'paste'
    dbvntax_id INTEGER,               -- original ID in dbvntax postgres DB
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_law_documents_v2_doc_type ON taxlegal.law_documents_v2(doc_type);
CREATE INDEX IF NOT EXISTS idx_law_documents_v2_is_priority ON taxlegal.law_documents_v2(is_priority);
CREATE INDEX IF NOT EXISTS idx_law_documents_v2_tags ON taxlegal.law_documents_v2 USING GIN(tags);

-- ============================================================
-- Regulation references — for matters and writing jobs
-- ============================================================
CREATE TABLE IF NOT EXISTS taxlegal.matter_regulations (
    id SERIAL PRIMARY KEY,
    matter_id INTEGER NOT NULL REFERENCES taxlegal.matters(id) ON DELETE CASCADE,
    law_doc_id INTEGER REFERENCES taxlegal.law_documents_v2(id),
    uploaded_content TEXT,            -- if user uploads directly without saving to law_documents
    uploaded_filename VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS taxlegal.writing_regulations (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES taxlegal.writing_jobs(id) ON DELETE CASCADE,
    law_doc_id INTEGER REFERENCES taxlegal.law_documents_v2(id),
    uploaded_content TEXT,
    uploaded_filename VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Document Analysis (Phân tích văn bản) — Module 3
-- ============================================================
CREATE TABLE IF NOT EXISTS taxlegal.doc_analysis_jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    uploaded_filename VARCHAR(500),
    uploaded_content TEXT,            -- extracted text from PDF/DOCX/TXT
    output_language VARCHAR(2) DEFAULT 'vi',
    actions JSONB DEFAULT '[]',       -- list of action slugs + custom prompts
    regulation_ids INTEGER[] DEFAULT '{}',
    uploaded_regulation_texts TEXT[] DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',  -- pending | analyzing | done | error
    results JSONB DEFAULT '{}',       -- {action_slug: result_text}
    bot_variant_id INTEGER,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Add review fields to writing_jobs
-- ============================================================
ALTER TABLE taxlegal.writing_jobs ADD COLUMN IF NOT EXISTS review_bot_variant_id INTEGER;
ALTER TABLE taxlegal.writing_jobs ADD COLUMN IF NOT EXISTS review_content TEXT;
ALTER TABLE taxlegal.writing_jobs ADD COLUMN IF NOT EXISTS review_status VARCHAR(50) DEFAULT 'none';
-- 'none' | 'pending' | 'reviewing' | 'done' | 'error'

-- ============================================================
-- Add category/topic to sample_writings for filtering
-- ============================================================
ALTER TABLE taxlegal.sample_writings ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE taxlegal.sample_writings ADD COLUMN IF NOT EXISTS topic VARCHAR(300);

-- ============================================================
-- sample_advices category/topic columns (table already exists above)
-- ============================================================
ALTER TABLE taxlegal.sample_advices ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE taxlegal.sample_advices ADD COLUMN IF NOT EXISTS topic VARCHAR(300);


-- ============================================================
-- v4 Architecture — new tables (safe: IF NOT EXISTS)
-- ============================================================

-- Skill versioning
ALTER TABLE taxlegal.skills ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE taxlegal.skills ADD COLUMN IF NOT EXISTS parent_skill_id INTEGER REFERENCES taxlegal.skills(id);

-- Bot node_type for workflow
ALTER TABLE taxlegal.bot_variants ADD COLUMN IF NOT EXISTS node_type VARCHAR(50) DEFAULT 'agent';

-- Workflow definitions
CREATE TABLE IF NOT EXISTS taxlegal.workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    practice_area VARCHAR(50) DEFAULT 'tax',
    graph_definition JSONB DEFAULT '{}',
    entry_node VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_workflow_definitions_slug ON taxlegal.workflow_definitions(slug);

-- Cases
CREATE TABLE IF NOT EXISTS taxlegal.cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matter_id INTEGER REFERENCES taxlegal.matters(id),
    title VARCHAR(500) NOT NULL,
    client_request TEXT NOT NULL,
    practice_area VARCHAR(100) DEFAULT 'tax',
    status VARCHAR(50) DEFAULT 'draft',
    workflow_definition_id UUID REFERENCES taxlegal.workflow_definitions(id),
    current_node VARCHAR(100),
    output_language VARCHAR(2) DEFAULT 'vi',
    priority VARCHAR(20) DEFAULT 'normal',
    metadata JSONB DEFAULT '{}',
    final_output TEXT,
    quality_score FLOAT,
    created_by INTEGER NOT NULL REFERENCES taxlegal.users(id),
    assigned_to INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_cases_status ON taxlegal.cases(status);
CREATE INDEX IF NOT EXISTS ix_cases_created_by ON taxlegal.cases(created_by);

-- Case events (audit trail)
CREATE TABLE IF NOT EXISTS taxlegal.case_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    node_name VARCHAR(100),
    actor VARCHAR(100),
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_case_events_case_id ON taxlegal.case_events(case_id);

-- Case versions (immutable snapshots)
CREATE TABLE IF NOT EXISTS taxlegal.case_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    snapshot JSONB NOT NULL,
    change_summary TEXT,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_case_versions_case_id ON taxlegal.case_versions(case_id);

-- Workflow nodes
CREATE TABLE IF NOT EXISTS taxlegal.workflow_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES taxlegal.workflow_definitions(id) ON DELETE CASCADE,
    node_id VARCHAR(100) NOT NULL,
    node_type VARCHAR(50) DEFAULT 'agent',
    label VARCHAR(200),
    bot_definition_id INTEGER REFERENCES taxlegal.bot_variants(id),
    skill_ids JSONB DEFAULT '[]',
    config JSONB DEFAULT '{}',
    position_x FLOAT,
    position_y FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workflow_id, node_id)
);
CREATE INDEX IF NOT EXISTS ix_workflow_nodes_workflow_id ON taxlegal.workflow_nodes(workflow_id);

-- Workflow edges
CREATE TABLE IF NOT EXISTS taxlegal.workflow_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES taxlegal.workflow_definitions(id) ON DELETE CASCADE,
    from_node VARCHAR(100) NOT NULL,
    to_node VARCHAR(100) NOT NULL,
    condition VARCHAR(200),
    label VARCHAR(200),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_workflow_edges_workflow_id ON taxlegal.workflow_edges(workflow_id);

-- Workflow runs
CREATE TABLE IF NOT EXISTS taxlegal.workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id),
    workflow_definition_id UUID REFERENCES taxlegal.workflow_definitions(id),
    workflow_version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending',
    current_node VARCHAR(100),
    state JSONB DEFAULT '{}',
    temporal_workflow_id VARCHAR(200),
    temporal_run_id VARCHAR(200),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_workflow_runs_case_id ON taxlegal.workflow_runs(case_id);
CREATE INDEX IF NOT EXISTS ix_workflow_runs_status ON taxlegal.workflow_runs(status);

-- Agent runs
CREATE TABLE IF NOT EXISTS taxlegal.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id UUID REFERENCES taxlegal.workflow_runs(id),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id),
    node_name VARCHAR(100) NOT NULL,
    bot_variant_slug VARCHAR(100),
    model_used VARCHAR(200),
    provider_used VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    input_state JSONB DEFAULT '{}',
    output_state JSONB DEFAULT '{}',
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    retrieval_queries JSONB DEFAULT '[]',
    citations_used JSONB DEFAULT '[]',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_agent_runs_case_id ON taxlegal.agent_runs(case_id);
CREATE INDEX IF NOT EXISTS ix_agent_runs_workflow_run_id ON taxlegal.agent_runs(workflow_run_id);

-- Skill versions
CREATE TABLE IF NOT EXISTS taxlegal.skill_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id INTEGER NOT NULL REFERENCES taxlegal.skills(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content_markdown TEXT NOT NULL,
    change_notes TEXT,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(skill_id, version_number)
);

-- Bot skill assignments
CREATE TABLE IF NOT EXISTS taxlegal.bot_skill_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_variant_id INTEGER NOT NULL REFERENCES taxlegal.bot_variants(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES taxlegal.skills(id) ON DELETE CASCADE,
    skill_version INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by INTEGER REFERENCES taxlegal.users(id),
    UNIQUE(bot_variant_id, skill_id)
);

-- Draft opinions
CREATE TABLE IF NOT EXISTS taxlegal.draft_opinions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id),
    agent_run_id UUID REFERENCES taxlegal.agent_runs(id),
    version_number INTEGER DEFAULT 1,
    content_markdown TEXT NOT NULL,
    content_html TEXT,
    word_count INTEGER,
    citations JSONB DEFAULT '[]',
    assumptions JSONB DEFAULT '[]',
    open_questions JSONB DEFAULT '[]',
    source_coverage_score FLOAT,
    has_insufficient_coverage BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_draft_opinions_case_id ON taxlegal.draft_opinions(case_id);

-- Review decisions
CREATE TABLE IF NOT EXISTS taxlegal.review_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id),
    agent_run_id UUID REFERENCES taxlegal.agent_runs(id),
    reviewer_role VARCHAR(50) NOT NULL,
    reviewer_id INTEGER REFERENCES taxlegal.users(id),
    decision VARCHAR(50) NOT NULL,
    technical_score FLOAT,
    risk_score FLOAT,
    issues_found JSONB DEFAULT '[]',
    corrections_required JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_review_decisions_case_id ON taxlegal.review_decisions(case_id);

-- Human approvals
CREATE TABLE IF NOT EXISTS taxlegal.human_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id),
    workflow_run_id UUID REFERENCES taxlegal.workflow_runs(id),
    requested_by VARCHAR(100),
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    approved_by INTEGER REFERENCES taxlegal.users(id),
    decision_notes TEXT,
    requested_at TIMESTAMP DEFAULT NOW(),
    decided_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_human_approvals_case_id ON taxlegal.human_approvals(case_id);

-- Citations
CREATE TABLE IF NOT EXISTS taxlegal.citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES taxlegal.cases(id),
    agent_run_id UUID REFERENCES taxlegal.agent_runs(id),
    source_type VARCHAR(50) NOT NULL,
    trust_level VARCHAR(20) DEFAULT 'high',
    law_identifier VARCHAR(300),
    article_reference VARCHAR(300),
    excerpt_text TEXT,
    source_url TEXT,
    retrieval_method VARCHAR(100),
    relevance_score FLOAT,
    is_verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_citations_case_id ON taxlegal.citations(case_id);

-- Retrieval queries (audit log)
CREATE TABLE IF NOT EXISTS taxlegal.retrieval_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES taxlegal.cases(id),
    agent_run_id UUID REFERENCES taxlegal.agent_runs(id),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) DEFAULT 'general',
    db_results_count INTEGER DEFAULT 0,
    used_fallback BOOLEAN DEFAULT FALSE,
    fallback_reason TEXT,
    insufficient_coverage BOOLEAN DEFAULT FALSE,
    results_summary JSONB DEFAULT '{}',
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Approval policies
CREATE TABLE IF NOT EXISTS taxlegal.approval_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    workflow_definition_id UUID REFERENCES taxlegal.workflow_definitions(id),
    trigger_conditions JSONB NOT NULL DEFAULT '{}',
    required_approvers JSONB DEFAULT '[]',
    timeout_hours INTEGER DEFAULT 48,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Task states (Redis-less durability fallback)
CREATE TABLE IF NOT EXISTS taxlegal.task_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id UUID REFERENCES taxlegal.workflow_runs(id),
    task_key VARCHAR(200) NOT NULL UNIQUE,
    state_data JSONB DEFAULT '{}',
    expires_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);
