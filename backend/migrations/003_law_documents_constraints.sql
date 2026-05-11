-- Migration 003: Add unique constraint on source_url for law_documents_v2
-- and is_priority index for priority-first retrieval
-- Idempotent: safe to run multiple times

-- Add unique index on source_url (only for non-null values)
CREATE UNIQUE INDEX IF NOT EXISTS ix_law_documents_v2_source_url
ON taxlegal.law_documents_v2(source_url)
WHERE source_url IS NOT NULL;

-- Index for priority-first retrieval ordering
CREATE INDEX IF NOT EXISTS ix_law_documents_v2_priority
ON taxlegal.law_documents_v2(is_priority DESC, created_at DESC);

-- Index for is_active filtering (used in all queries)
CREATE INDEX IF NOT EXISTS ix_law_documents_v2_active
ON taxlegal.law_documents_v2(is_active) WHERE is_active = TRUE;

-- Add priority_level column if not exists
ALTER TABLE taxlegal.law_documents_v2 ADD COLUMN IF NOT EXISTS priority_level SMALLINT DEFAULT 1;

COMMENT ON TABLE taxlegal.law_documents_v2 IS
  'Primary law document store. is_priority=TRUE docs are injected first into AI prompts.';
