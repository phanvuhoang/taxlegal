-- Migration 004: Add tax_types column + doc_type enum + retrieval indexes
-- Idempotent — safe to run multiple times

-- 1. Add tax_types array (sắc thuế: GTGT, TNDN, TNCN, FCT, TTDB, XNK, TP, HKD, HOA_DON, THUE_QT)
ALTER TABLE taxlegal.law_documents_v2 ADD COLUMN IF NOT EXISTS tax_types TEXT[] DEFAULT '{}';

-- 2. Add sac_thue as alias (mirrors dbvntax naming) — same data, different view
--    We keep one column: tax_types. dbvntax sac_thue maps to this on import.

-- 3. Add effective_status (con_hieu_luc | het_hieu_luc | chua_co_hieu_luc)
ALTER TABLE taxlegal.law_documents_v2 ADD COLUMN IF NOT EXISTS effective_status VARCHAR(30) DEFAULT 'con_hieu_luc';

-- 4. Add link_tvpl for direct source link
ALTER TABLE taxlegal.law_documents_v2 ADD COLUMN IF NOT EXISTS link_tvpl TEXT;

-- 5. Add importance (1=highest, 5=lowest) for sort ordering
ALTER TABLE taxlegal.law_documents_v2 ADD COLUMN IF NOT EXISTS importance SMALLINT DEFAULT 3;

-- 6. GIN index on tax_types for fast array containment queries
CREATE INDEX IF NOT EXISTS ix_law_documents_v2_tax_types
ON taxlegal.law_documents_v2 USING GIN(tax_types);

-- 7. FTS index for Vietnamese-friendly search (simple config + unaccent)
CREATE INDEX IF NOT EXISTS ix_law_documents_v2_fts
ON taxlegal.law_documents_v2 USING GIN (
    to_tsvector('simple',
        coalesce(title, '') || ' ' ||
        coalesce(doc_number, '') || ' ' ||
        coalesce(array_to_string(tax_types, ' '), '') || ' ' ||
        coalesce(left(content_text, 10000), '')
    )
);

-- 8. Index on doc_type for filtering Luật/NĐ/TT
CREATE INDEX IF NOT EXISTS ix_law_documents_v2_doc_type_active
ON taxlegal.law_documents_v2(doc_type, is_active)
WHERE is_active = TRUE;

-- 9. Composite index: priority + tax_types ordering
CREATE INDEX IF NOT EXISTS ix_law_documents_v2_priority_importance
ON taxlegal.law_documents_v2(is_priority DESC, importance ASC, issued_date DESC NULLS LAST)
WHERE is_active = TRUE;

COMMENT ON COLUMN taxlegal.law_documents_v2.tax_types IS
    'Array of tax type codes: GTGT, TNDN, TNCN, FCT, TTDB, XNK, TP, HKD, HOA_DON, THUE_QT, THUE_QT';
COMMENT ON COLUMN taxlegal.law_documents_v2.effective_status IS
    'con_hieu_luc | het_hieu_luc | chua_co_hieu_luc';
COMMENT ON COLUMN taxlegal.law_documents_v2.importance IS
    '1=highest priority law (e.g. Luật), 5=lowest (Công văn)';
