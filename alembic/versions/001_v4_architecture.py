"""v4 architecture — new tables, indexes, and column additions

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Ensure taxlegal schema exists ─────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS taxlegal")

    # ── workflow_definitions ──────────────────────────────────────────────────
    op.create_table(
        "workflow_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_default", sa.Boolean, server_default="false"),
        sa.Column("practice_area", sa.String(50), server_default="tax"),
        sa.Column("graph_definition", postgresql.JSONB, server_default="{}"),
        sa.Column("entry_node", sa.String(100), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_workflow_definitions_slug", "workflow_definitions", ["slug"], schema="taxlegal")

    # ── cases ─────────────────────────────────────────────────────────────────
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("matter_id", sa.Integer, sa.ForeignKey("taxlegal.matters.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("client_request", sa.Text, nullable=False),
        sa.Column("practice_area", sa.String(100), server_default="tax"),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_definitions.id"), nullable=True),
        sa.Column("current_node", sa.String(100), nullable=True),
        sa.Column("output_language", sa.String(2), server_default="vi"),
        sa.Column("priority", sa.String(20), server_default="normal"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("final_output", sa.Text, nullable=True),
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=False),
        sa.Column("assigned_to", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_cases_status", "cases", ["status"], schema="taxlegal")
    op.create_index("ix_cases_created_by", "cases", ["created_by"], schema="taxlegal")
    op.create_index("ix_cases_workflow_definition_id", "cases", ["workflow_definition_id"], schema="taxlegal")

    # ── case_events ───────────────────────────────────────────────────────────
    op.create_table(
        "case_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("node_name", sa.String(100), nullable=True),
        sa.Column("actor", sa.String(100), nullable=True),
        sa.Column("data", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_case_events_case_id", "case_events", ["case_id"], schema="taxlegal")

    # ── case_versions ─────────────────────────────────────────────────────────
    op.create_table(
        "case_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("snapshot", postgresql.JSONB, nullable=False),
        sa.Column("change_summary", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_case_versions_case_id", "case_versions", ["case_id"], schema="taxlegal")

    # ── workflow_nodes ────────────────────────────────────────────────────────
    op.create_table(
        "workflow_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_id", sa.String(100), nullable=False),
        sa.Column("node_type", sa.String(50), server_default="agent"),
        sa.Column("label", sa.String(200), nullable=True),
        sa.Column("bot_definition_id", sa.Integer, sa.ForeignKey("taxlegal.bot_variants.id"), nullable=True),
        sa.Column("skill_ids", postgresql.JSONB, server_default="[]"),
        sa.Column("config", postgresql.JSONB, server_default="{}"),
        sa.Column("position_x", sa.Float, nullable=True),
        sa.Column("position_y", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("workflow_id", "node_id", name="uq_workflow_node"),
        schema="taxlegal",
    )
    op.create_index("ix_workflow_nodes_workflow_id", "workflow_nodes", ["workflow_id"], schema="taxlegal")

    # ── workflow_edges ────────────────────────────────────────────────────────
    op.create_table(
        "workflow_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_node", sa.String(100), nullable=False),
        sa.Column("to_node", sa.String(100), nullable=False),
        sa.Column("condition", sa.String(200), nullable=True),
        sa.Column("label", sa.String(200), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_workflow_edges_workflow_id", "workflow_edges", ["workflow_id"], schema="taxlegal")

    # ── workflow_runs ─────────────────────────────────────────────────────────
    op.create_table(
        "workflow_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=False),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_definitions.id"), nullable=False),
        sa.Column("workflow_version", sa.Integer, server_default="1"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("current_node", sa.String(100), nullable=True),
        sa.Column("state", postgresql.JSONB, server_default="{}"),
        sa.Column("temporal_workflow_id", sa.String(200), nullable=True),
        sa.Column("temporal_run_id", sa.String(200), nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_workflow_runs_case_id", "workflow_runs", ["case_id"], schema="taxlegal")
    op.create_index("ix_workflow_runs_status", "workflow_runs", ["status"], schema="taxlegal")
    op.create_index("ix_workflow_runs_workflow_definition_id", "workflow_runs", ["workflow_definition_id"], schema="taxlegal")

    # ── agent_runs ────────────────────────────────────────────────────────────
    op.create_table(
        "agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_runs.id"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=False),
        sa.Column("node_name", sa.String(100), nullable=False),
        sa.Column("bot_variant_slug", sa.String(100), nullable=True),
        sa.Column("model_used", sa.String(200), nullable=True),
        sa.Column("provider_used", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("input_state", postgresql.JSONB, server_default="{}"),
        sa.Column("output_state", postgresql.JSONB, server_default="{}"),
        sa.Column("prompt_tokens", sa.Integer, server_default="0"),
        sa.Column("completion_tokens", sa.Integer, server_default="0"),
        sa.Column("retrieval_queries", postgresql.JSONB, server_default="[]"),
        sa.Column("citations_used", postgresql.JSONB, server_default="[]"),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_agent_runs_workflow_run_id", "agent_runs", ["workflow_run_id"], schema="taxlegal")
    op.create_index("ix_agent_runs_case_id", "agent_runs", ["case_id"], schema="taxlegal")
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"], schema="taxlegal")

    # ── skill_versions ────────────────────────────────────────────────────────
    op.create_table(
        "skill_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", sa.Integer,
                  sa.ForeignKey("taxlegal.skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("content_markdown", sa.Text, nullable=False),
        sa.Column("change_notes", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("skill_id", "version_number", name="uq_skill_version"),
        schema="taxlegal",
    )
    op.create_index("ix_skill_versions_skill_id", "skill_versions", ["skill_id"], schema="taxlegal")

    # ── bot_skill_assignments ─────────────────────────────────────────────────
    op.create_table(
        "bot_skill_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bot_variant_id", sa.Integer,
                  sa.ForeignKey("taxlegal.bot_variants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer,
                  sa.ForeignKey("taxlegal.skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_version", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("assigned_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("assigned_by", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.UniqueConstraint("bot_variant_id", "skill_id", name="uq_bot_skill"),
        schema="taxlegal",
    )
    op.create_index("ix_bot_skill_assignments_bot_variant_id", "bot_skill_assignments", ["bot_variant_id"], schema="taxlegal")
    op.create_index("ix_bot_skill_assignments_skill_id", "bot_skill_assignments", ["skill_id"], schema="taxlegal")

    # ── draft_opinions ────────────────────────────────────────────────────────
    op.create_table(
        "draft_opinions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=False),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.agent_runs.id"), nullable=True),
        sa.Column("version_number", sa.Integer, server_default="1"),
        sa.Column("content_markdown", sa.Text, nullable=False),
        sa.Column("content_html", sa.Text, nullable=True),
        sa.Column("word_count", sa.Integer, nullable=True),
        sa.Column("citations", postgresql.JSONB, server_default="[]"),
        sa.Column("assumptions", postgresql.JSONB, server_default="[]"),
        sa.Column("open_questions", postgresql.JSONB, server_default="[]"),
        sa.Column("source_coverage_score", sa.Float, nullable=True),
        sa.Column("has_insufficient_coverage", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_draft_opinions_case_id", "draft_opinions", ["case_id"], schema="taxlegal")
    op.create_index("ix_draft_opinions_agent_run_id", "draft_opinions", ["agent_run_id"], schema="taxlegal")

    # ── review_decisions ──────────────────────────────────────────────────────
    op.create_table(
        "review_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=False),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.agent_runs.id"), nullable=True),
        sa.Column("reviewer_role", sa.String(50), nullable=True),
        sa.Column("reviewer_id", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.Column("decision", sa.String(50), nullable=True),
        sa.Column("technical_score", sa.Float, nullable=True),
        sa.Column("risk_score", sa.Float, nullable=True),
        sa.Column("issues_found", postgresql.JSONB, server_default="[]"),
        sa.Column("corrections_required", postgresql.JSONB, server_default="[]"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_review_decisions_case_id", "review_decisions", ["case_id"], schema="taxlegal")
    op.create_index("ix_review_decisions_agent_run_id", "review_decisions", ["agent_run_id"], schema="taxlegal")

    # ── human_approvals ───────────────────────────────────────────────────────
    op.create_table(
        "human_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=False),
        sa.Column("workflow_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_runs.id"), nullable=True),
        sa.Column("requested_by", sa.String(100), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("approved_by", sa.Integer, sa.ForeignKey("taxlegal.users.id"), nullable=True),
        sa.Column("decision_notes", sa.Text, nullable=True),
        sa.Column("requested_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("decided_at", sa.DateTime, nullable=True),
        schema="taxlegal",
    )
    op.create_index("ix_human_approvals_case_id", "human_approvals", ["case_id"], schema="taxlegal")
    op.create_index("ix_human_approvals_workflow_run_id", "human_approvals", ["workflow_run_id"], schema="taxlegal")
    op.create_index("ix_human_approvals_status", "human_approvals", ["status"], schema="taxlegal")

    # ── citations ─────────────────────────────────────────────────────────────
    op.create_table(
        "citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=False),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.agent_runs.id"), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("trust_level", sa.String(20), server_default="high"),
        sa.Column("law_identifier", sa.String(300), nullable=True),
        sa.Column("article_reference", sa.String(300), nullable=True),
        sa.Column("excerpt_text", sa.Text, nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("retrieval_method", sa.String(100), nullable=True),
        sa.Column("relevance_score", sa.Float, nullable=True),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_citations_case_id", "citations", ["case_id"], schema="taxlegal")
    op.create_index("ix_citations_agent_run_id", "citations", ["agent_run_id"], schema="taxlegal")
    op.create_index("ix_citations_source_type", "citations", ["source_type"], schema="taxlegal")

    # ── retrieval_queries ─────────────────────────────────────────────────────
    op.create_table(
        "retrieval_queries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.cases.id"), nullable=True),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.agent_runs.id"), nullable=True),
        sa.Column("query_text", sa.Text, nullable=False),
        sa.Column("query_type", sa.String(50), nullable=True),
        sa.Column("db_results_count", sa.Integer, server_default="0"),
        sa.Column("used_fallback", sa.Boolean, server_default="false"),
        sa.Column("fallback_reason", sa.Text, nullable=True),
        sa.Column("insufficient_coverage", sa.Boolean, server_default="false"),
        sa.Column("results_summary", postgresql.JSONB, server_default="{}"),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_retrieval_queries_case_id", "retrieval_queries", ["case_id"], schema="taxlegal")
    op.create_index("ix_retrieval_queries_agent_run_id", "retrieval_queries", ["agent_run_id"], schema="taxlegal")

    # ── approval_policies ─────────────────────────────────────────────────────
    op.create_table(
        "approval_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_definitions.id"), nullable=True),
        sa.Column("trigger_conditions", postgresql.JSONB, nullable=False),
        sa.Column("required_approvers", postgresql.JSONB, server_default="[]"),
        sa.Column("timeout_hours", sa.Integer, server_default="48"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_approval_policies_workflow_definition_id", "approval_policies", ["workflow_definition_id"], schema="taxlegal")

    # ── task_states ───────────────────────────────────────────────────────────
    op.create_table(
        "task_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("taxlegal.workflow_runs.id"), nullable=False),
        sa.Column("task_key", sa.String(200), nullable=False, unique=True),
        sa.Column("state_data", postgresql.JSONB, server_default="{}"),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        schema="taxlegal",
    )
    op.create_index("ix_task_states_workflow_run_id", "task_states", ["workflow_run_id"], schema="taxlegal")

    # ── Add columns to taxlegal.skills ────────────────────────────────────────
    op.add_column(
        "skills",
        sa.Column("version_number", sa.Integer, server_default="1"),
        schema="taxlegal",
    )
    op.add_column(
        "skills",
        sa.Column("parent_skill_id", sa.Integer,
                  sa.ForeignKey("taxlegal.skills.id"), nullable=True),
        schema="taxlegal",
    )

    # ── Add column to taxlegal.bot_variants ───────────────────────────────────
    op.add_column(
        "bot_variants",
        sa.Column("node_type", sa.String(50), server_default="agent"),
        schema="taxlegal",
    )


def downgrade() -> None:
    # Remove added columns
    op.drop_column("bot_variants", "node_type", schema="taxlegal")
    op.drop_column("skills", "parent_skill_id", schema="taxlegal")
    op.drop_column("skills", "version_number", schema="taxlegal")

    # Drop new tables in reverse dependency order
    op.drop_index("ix_task_states_workflow_run_id", table_name="task_states", schema="taxlegal")
    op.drop_table("task_states", schema="taxlegal")

    op.drop_index("ix_approval_policies_workflow_definition_id", table_name="approval_policies", schema="taxlegal")
    op.drop_table("approval_policies", schema="taxlegal")

    op.drop_index("ix_retrieval_queries_agent_run_id", table_name="retrieval_queries", schema="taxlegal")
    op.drop_index("ix_retrieval_queries_case_id", table_name="retrieval_queries", schema="taxlegal")
    op.drop_table("retrieval_queries", schema="taxlegal")

    op.drop_index("ix_citations_source_type", table_name="citations", schema="taxlegal")
    op.drop_index("ix_citations_agent_run_id", table_name="citations", schema="taxlegal")
    op.drop_index("ix_citations_case_id", table_name="citations", schema="taxlegal")
    op.drop_table("citations", schema="taxlegal")

    op.drop_index("ix_human_approvals_status", table_name="human_approvals", schema="taxlegal")
    op.drop_index("ix_human_approvals_workflow_run_id", table_name="human_approvals", schema="taxlegal")
    op.drop_index("ix_human_approvals_case_id", table_name="human_approvals", schema="taxlegal")
    op.drop_table("human_approvals", schema="taxlegal")

    op.drop_index("ix_review_decisions_agent_run_id", table_name="review_decisions", schema="taxlegal")
    op.drop_index("ix_review_decisions_case_id", table_name="review_decisions", schema="taxlegal")
    op.drop_table("review_decisions", schema="taxlegal")

    op.drop_index("ix_draft_opinions_agent_run_id", table_name="draft_opinions", schema="taxlegal")
    op.drop_index("ix_draft_opinions_case_id", table_name="draft_opinions", schema="taxlegal")
    op.drop_table("draft_opinions", schema="taxlegal")

    op.drop_index("ix_bot_skill_assignments_skill_id", table_name="bot_skill_assignments", schema="taxlegal")
    op.drop_index("ix_bot_skill_assignments_bot_variant_id", table_name="bot_skill_assignments", schema="taxlegal")
    op.drop_table("bot_skill_assignments", schema="taxlegal")

    op.drop_index("ix_skill_versions_skill_id", table_name="skill_versions", schema="taxlegal")
    op.drop_table("skill_versions", schema="taxlegal")

    op.drop_index("ix_agent_runs_status", table_name="agent_runs", schema="taxlegal")
    op.drop_index("ix_agent_runs_case_id", table_name="agent_runs", schema="taxlegal")
    op.drop_index("ix_agent_runs_workflow_run_id", table_name="agent_runs", schema="taxlegal")
    op.drop_table("agent_runs", schema="taxlegal")

    op.drop_index("ix_workflow_runs_workflow_definition_id", table_name="workflow_runs", schema="taxlegal")
    op.drop_index("ix_workflow_runs_status", table_name="workflow_runs", schema="taxlegal")
    op.drop_index("ix_workflow_runs_case_id", table_name="workflow_runs", schema="taxlegal")
    op.drop_table("workflow_runs", schema="taxlegal")

    op.drop_index("ix_workflow_edges_workflow_id", table_name="workflow_edges", schema="taxlegal")
    op.drop_table("workflow_edges", schema="taxlegal")

    op.drop_index("ix_workflow_nodes_workflow_id", table_name="workflow_nodes", schema="taxlegal")
    op.drop_table("workflow_nodes", schema="taxlegal")

    op.drop_index("ix_case_versions_case_id", table_name="case_versions", schema="taxlegal")
    op.drop_table("case_versions", schema="taxlegal")

    op.drop_index("ix_case_events_case_id", table_name="case_events", schema="taxlegal")
    op.drop_table("case_events", schema="taxlegal")

    op.drop_index("ix_cases_workflow_definition_id", table_name="cases", schema="taxlegal")
    op.drop_index("ix_cases_created_by", table_name="cases", schema="taxlegal")
    op.drop_index("ix_cases_status", table_name="cases", schema="taxlegal")
    op.drop_table("cases", schema="taxlegal")

    op.drop_index("ix_workflow_definitions_slug", table_name="workflow_definitions", schema="taxlegal")
    op.drop_table("workflow_definitions", schema="taxlegal")
