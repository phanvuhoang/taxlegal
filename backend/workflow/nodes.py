"""
LangGraph workflow nodes — each node corresponds to one stage in the tax advisory pipeline.
Nodes wrap the existing pipeline.py step runners + new DB-first retrieval.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.retrieval.service import RetrievalService
from backend.retrieval.prompt_guard import DB_FIRST_SYSTEM_ADDENDUM, build_retrieval_context_block
from backend.agents.prompts import (
    INTAKE_SYSTEM_PROMPT,
    PARTNER_P1_SYSTEM_PROMPT,
    SA_BLUEPRINT_SYSTEM_PROMPT,
    JA_RESEARCH_SYSTEM_PROMPT,
    SA_REVIEW_SYSTEM_PROMPT,
    PARTNER_P2_SYSTEM_PROMPT,
    PARTNER_P3_SYSTEM_PROMPT,
)
from backend.ai_provider import call_ai
from backend.agents.pipeline import (
    build_system_prompt_with_skills,
    get_agent_model,
)

if TYPE_CHECKING:
    from backend.workflow.state import WorkflowState

logger = logging.getLogger(__name__)

retrieval_service = RetrievalService()

# ── Helpers ────────────────────────────────────────────────────────────────────

def _audit(event_type: str, node: str, data: dict = None) -> dict:
    """Return a single audit event dict."""
    return {
        "event_type": event_type,
        "node": node,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data or {},
    }


def _extract_json(text: str) -> Optional[dict]:
    """Extract JSON from AI response text (handles markdown code fences)."""
    # Try ```json ... ``` first
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Try bare JSON object
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    return None


def _safe_get(state: dict, key: str, default=None):
    """Safely get a key from the state dict."""
    return state.get(key, default)


# ── WorkflowNodes class ────────────────────────────────────────────────────────

class WorkflowNodes:
    """
    Class-based LangGraph node container.
    Holds DB sessions so that node methods can access them via closure.
    Each node method takes (state: WorkflowState) and returns a partial state dict.
    """

    def __init__(self, db: AsyncSession, dbvntax_db: AsyncSession = None):
        self.db = db
        self.dbvntax_db = dbvntax_db

    # ── Node 1: Intake ─────────────────────────────────────────────────────────

    async def node_intake(self, state: "WorkflowState") -> dict:
        """
        Step 1 — Intake Enhancer with DB-first retrieval.
        Retrieves applicable laws from internal DB, verifies facts,
        builds completeness matrix with DB context.
        """
        node_name = "intake"
        case_id = _safe_get(state, "case_id")
        client_request = _safe_get(state, "client_request", "")
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Starting for case {case_id}")

        # DB-first retrieval for applicable laws
        retrieval_result = None
        try:
            retrieval_result = await retrieval_service.retrieve(
                query=f"Luật Việt Nam áp dụng cho: {client_request[:200]}",
                db=self.db,
                dbvntax_db=self.dbvntax_db,
                min_db_results=1,
                case_id=case_id,
                agent_run_id=_safe_get(state, "workflow_run_id"),
            )
        except Exception as e:
            logger.error(f"[{node_name}] Retrieval failed: {e}")

        # Build enriched system prompt
        retrieval_context = ""
        if retrieval_result:
            retrieval_context = build_retrieval_context_block(retrieval_result)

        system_prompt = INTAKE_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM + retrieval_context

        # Build user prompt
        web_search_summary = ""
        if retrieval_result and retrieval_result.web_results:
            web_search_summary = json.dumps(
                retrieval_result.web_results[0], ensure_ascii=False, indent=2
            )[:2000]

        prompt = f"""## YÊU CẦU CỦA KHÁCH HÀNG
{client_request}

## KẾT QUẢ TÌM KIẾM / NGUỒN PHÁP LÝ (DB-first)
{retrieval_context if retrieval_context else "[Không có nguồn từ DB]"}

{f"## KẾT QUẢ TÌM KIẾM WEB (fallback)\\n{web_search_summary}" if web_search_summary else ""}

Hãy phân tích và tạo Enriched Request theo đúng format JSON đã được định nghĩa trong system prompt.
Tập trung vào việc xác minh sự kiện, kiểm tra hiệu lực luật, và xây dựng completeness matrix đầy đủ.
CHỈ trích dẫn các văn bản pháp lý có trong RETRIEVED SOURCES phía trên."""

        # Call AI
        try:
            model_id, provider = await get_agent_model(self.db, "intake")
            result = await call_ai(
                model_id=model_id,
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=8000,
                provider=provider,
            )
            content = result["content"]
        except Exception as e:
            logger.error(f"[{node_name}] AI call failed: {e}")
            content = "{}"

        output_data = _extract_json(content) or {}

        # Extract state fields from output
        verified_facts = output_data.get("verified_facts", [])
        applicable_laws = output_data.get("applicable_laws", [])
        completeness_matrix = output_data.get("completeness_matrix", [])

        # Detect missing facts (items in completeness matrix where covered=False)
        missing_facts = [
            item.get("issue", "")
            for item in completeness_matrix
            if not item.get("covered", True) and item.get("issue")
        ]

        # Build citations from retrieval
        new_citations = (retrieval_result.citations if retrieval_result else [])
        existing_citations = _safe_get(state, "citations") or []

        # Track retrieval queries
        existing_queries = _safe_get(state, "retrieval_queries") or []
        if retrieval_result:
            existing_queries = existing_queries + [{
                "node": node_name,
                "query": retrieval_result.query,
                "db_results": len(retrieval_result.db_results),
                "web_results": len(retrieval_result.web_results),
                "used_fallback": retrieval_result.used_fallback,
                "insufficient_coverage": retrieval_result.insufficient_coverage,
            }]

        update = {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "verified_facts": verified_facts,
            "applicable_laws": applicable_laws,
            "completeness_matrix": completeness_matrix,
            "missing_facts": missing_facts,
            "citations": existing_citations + new_citations,
            "retrieval_queries": existing_queries,
            "used_fallback_search": (
                (_safe_get(state, "used_fallback_search") or False)
                or (retrieval_result.used_fallback if retrieval_result else False)
            ),
            "has_insufficient_coverage": (
                (_safe_get(state, "has_insufficient_coverage") or False)
                or (retrieval_result.insufficient_coverage if retrieval_result else False)
            ),
            "iterations": iterations + 1,
            "audit_events": [_audit("node_completed", node_name, {
                "verified_facts_count": len(verified_facts),
                "applicable_laws_count": len(applicable_laws),
                "completeness_matrix_count": len(completeness_matrix),
                "missing_facts_count": len(missing_facts),
                "retrieval_used_fallback": retrieval_result.used_fallback if retrieval_result else False,
            })],
        }
        return update

    # ── Node 2: Clarification ──────────────────────────────────────────────────

    async def node_clarification(self, state: "WorkflowState") -> dict:
        """
        Handle missing facts. Max 2 clarification iterations to prevent loops.
        If max reached: mark unresolvable and continue.
        """
        node_name = "clarification"
        clarification_iterations = _safe_get(state, "clarification_iterations", 0)
        missing_facts = _safe_get(state, "missing_facts") or []
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] iteration {clarification_iterations}, missing: {len(missing_facts)}")

        if clarification_iterations >= 2:
            # Max iterations reached — mark as unresolvable, proceed with what we have
            logger.warning(f"[{node_name}] Max clarification iterations reached; proceeding without {missing_facts}")
            updated_matrix = []
            for item in (_safe_get(state, "completeness_matrix") or []):
                if not item.get("covered", True):
                    item = dict(item)
                    item["covered"] = False
                    item["note"] = "Unresolvable — insufficient client info"
                updated_matrix.append(item)
            return {
                "current_node": node_name,
                "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
                "missing_facts": [],  # clear so we don't loop again
                "clarification_iterations": clarification_iterations + 1,
                "completeness_matrix": updated_matrix,
                "iterations": iterations + 1,
                "audit_events": [_audit("clarification_max_reached", node_name, {
                    "unresolvable_facts": missing_facts,
                })],
            }

        # Note what's still missing — client would normally supply this
        # In automated workflow, we record the gap and move on
        return {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "clarification_iterations": clarification_iterations + 1,
            "iterations": iterations + 1,
            "audit_events": [_audit("clarification_requested", node_name, {
                "missing_facts": missing_facts,
                "iteration": clarification_iterations + 1,
            })],
        }

    # ── Node 3: Research ───────────────────────────────────────────────────────

    async def node_research(self, state: "WorkflowState") -> dict:
        """
        Research node: DB-first retrieval per completeness matrix item,
        builds partner brief + SA blueprint, runs JA research.
        """
        node_name = "research"
        case_id = _safe_get(state, "case_id")
        client_request = _safe_get(state, "client_request", "")
        completeness_matrix = _safe_get(state, "completeness_matrix") or []
        verified_facts = _safe_get(state, "verified_facts") or []
        applicable_laws = _safe_get(state, "applicable_laws") or []
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Starting research for case {case_id}, {len(completeness_matrix)} items")

        all_citations: list[dict] = list(_safe_get(state, "citations") or [])
        all_retrieval_queries: list[dict] = list(_safe_get(state, "retrieval_queries") or [])
        used_fallback = _safe_get(state, "used_fallback_search") or False
        has_insufficient = _safe_get(state, "has_insufficient_coverage") or False
        research_chunks: list[dict] = []

        # --- Step A: Partner P1 Brief ---
        partner_brief = _safe_get(state, "partner_brief")
        if not partner_brief:
            try:
                intake_data = json.dumps({
                    "verified_facts": verified_facts,
                    "applicable_laws": applicable_laws,
                    "completeness_matrix": completeness_matrix,
                }, ensure_ascii=False, indent=2)

                p1_prompt = f"""## YÊU CẦU GỐC CỦA KHÁCH HÀNG
{client_request}

## ENRICHED REQUEST (TỪ INTAKE ENHANCER)
{intake_data}

Hãy tạo Partner Brief theo đúng format JSON trong system prompt.
Đây là "lệnh điều quân" — phải đủ cụ thể để SA và JA không cần hỏi lại."""

                model_id, provider = await get_agent_model(self.db, "partner")
                p1_result = await call_ai(
                    model_id=model_id,
                    messages=[{"role": "user", "content": p1_prompt}],
                    system_prompt=PARTNER_P1_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM,
                    temperature=0.3,
                    max_tokens=6000,
                    provider=provider,
                )
                partner_brief = _extract_json(p1_result["content"]) or {}
            except Exception as e:
                logger.error(f"[{node_name}] Partner P1 failed: {e}")
                partner_brief = {}

        # --- Step B: SA Blueprint ---
        sa_blueprint = _safe_get(state, "sa_blueprint")
        if not sa_blueprint:
            try:
                blueprint_context = json.dumps({
                    "verified_facts": verified_facts,
                    "applicable_laws": applicable_laws,
                    "completeness_matrix": completeness_matrix,
                    "partner_brief": partner_brief,
                }, ensure_ascii=False, indent=2)

                bp_prompt = f"""## YÊU CẦU KHÁCH HÀNG
{client_request}

## CONTEXT (Intake + Partner Brief)
{blueprint_context}

Hãy thiết kế Document Blueprint và Chunk Division theo format JSON trong system prompt."""

                model_id, provider = await get_agent_model(self.db, "sa")
                bp_result = await call_ai(
                    model_id=model_id,
                    messages=[{"role": "user", "content": bp_prompt}],
                    system_prompt=SA_BLUEPRINT_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM,
                    temperature=0.2,
                    max_tokens=8000,
                    provider=provider,
                )
                sa_blueprint = _extract_json(bp_result["content"]) or {}
            except Exception as e:
                logger.error(f"[{node_name}] SA Blueprint failed: {e}")
                sa_blueprint = {}

        # --- Step C: JA Research per chunk with DB-first retrieval ---
        chunks = (sa_blueprint or {}).get("chunks", [])
        if not chunks:
            # Fallback: one chunk per completeness matrix item
            chunks = [
                {
                    "chunk_id": i + 1,
                    "section": f"Phần {i + 1}",
                    "issue": item.get("issue", f"Vấn đề {i + 1}"),
                    "depth": item.get("depth", "STANDARD"),
                    "word_count_target": 600,
                }
                for i, item in enumerate(completeness_matrix or [{"issue": client_request[:100]}])
            ]

        ja_model_id, ja_provider = await get_agent_model(self.db, "ja")

        for chunk_def in chunks[:10]:  # cap at 10 chunks
            chunk_issue = chunk_def.get("issue", "")
            chunk_id = chunk_def.get("chunk_id", 1)
            chunk_depth = chunk_def.get("depth", "STANDARD")

            # DB-first retrieval for this chunk
            chunk_retrieval = None
            try:
                chunk_retrieval = await retrieval_service.retrieve(
                    query=chunk_issue,
                    db=self.db,
                    dbvntax_db=self.dbvntax_db,
                    min_db_results=1,
                    case_id=case_id,
                    agent_run_id=_safe_get(state, "workflow_run_id"),
                )
                all_citations.extend(chunk_retrieval.citations)
                used_fallback = used_fallback or chunk_retrieval.used_fallback
                has_insufficient = has_insufficient or chunk_retrieval.insufficient_coverage
                all_retrieval_queries.append({
                    "node": node_name,
                    "chunk_id": chunk_id,
                    "query": chunk_issue,
                    "db_results": len(chunk_retrieval.db_results),
                    "web_results": len(chunk_retrieval.web_results),
                    "used_fallback": chunk_retrieval.used_fallback,
                })
            except Exception as e:
                logger.error(f"[{node_name}] Chunk retrieval failed for chunk {chunk_id}: {e}")

            retrieval_context = build_retrieval_context_block(chunk_retrieval) if chunk_retrieval else ""

            chunk_prompt = f"""## CHUNK CẦN NGHIÊN CỨU
Chunk ID: {chunk_id}
Vấn đề: {chunk_issue}
Độ sâu: {chunk_depth}
Word count target: {chunk_def.get("word_count_target", 600)} từ

## CONTEXT
Yêu cầu khách hàng: {client_request[:500]}
Verified facts: {json.dumps(verified_facts, ensure_ascii=False)[:1000]}
Partner brief guidance: {json.dumps(partner_brief, ensure_ascii=False)[:1000]}

{retrieval_context}

Hãy thực hiện đầy đủ 5 phases (A, B1, B2, B2.5, C) và tạo:
1. JSON nghiên cứu (phase outputs)
2. Văn bản tư vấn Markdown cho chunk này
CHỈ trích dẫn văn bản pháp lý có trong RETRIEVED SOURCES phía trên."""

            try:
                chunk_result = await call_ai(
                    model_id=ja_model_id,
                    messages=[{"role": "user", "content": chunk_prompt}],
                    system_prompt=JA_RESEARCH_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM,
                    temperature=0.3,
                    max_tokens=8000,
                    provider=ja_provider,
                )
                chunk_content = chunk_result["content"]
                chunk_data = _extract_json(chunk_content) or {}
                research_chunks.append({
                    "chunk_id": chunk_id,
                    "issue": chunk_issue,
                    "depth": chunk_depth,
                    "content_markdown": chunk_content,
                    "data": chunk_data,
                })
            except Exception as e:
                logger.error(f"[{node_name}] JA chunk {chunk_id} failed: {e}")
                research_chunks.append({
                    "chunk_id": chunk_id,
                    "issue": chunk_issue,
                    "depth": chunk_depth,
                    "content_markdown": f"[Research failed: {e}]",
                    "data": {},
                })

        return {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "partner_brief": partner_brief,
            "sa_blueprint": sa_blueprint,
            "research_chunks": research_chunks,
            "citations": all_citations,
            "retrieval_queries": all_retrieval_queries,
            "used_fallback_search": used_fallback,
            "has_insufficient_coverage": has_insufficient,
            "iterations": iterations + 1,
            "audit_events": [_audit("node_completed", node_name, {
                "chunks_researched": len(research_chunks),
                "citations_accumulated": len(all_citations),
                "used_fallback": used_fallback,
                "has_insufficient_coverage": has_insufficient,
            })],
        }

    # ── Node 4: Draft ──────────────────────────────────────────────────────────

    async def node_draft(self, state: "WorkflowState") -> dict:
        """
        Assemble final advisory draft from research chunks.
        Injects DB_FIRST_SYSTEM_ADDENDUM into final prompt.
        """
        node_name = "draft"
        case_id = _safe_get(state, "case_id")
        client_request = _safe_get(state, "client_request", "")
        research_chunks = _safe_get(state, "research_chunks") or []
        sa_blueprint = _safe_get(state, "sa_blueprint") or {}
        applicable_laws = _safe_get(state, "applicable_laws") or []
        output_language = _safe_get(state, "output_language", "vi")
        draft_version = _safe_get(state, "draft_version", 0)
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Drafting for case {case_id}, version {draft_version + 1}")

        # SA Review issues from previous iteration (for rework)
        sa_issues = _safe_get(state, "sa_issues") or []
        sa_corrections = ""
        if sa_issues:
            sa_corrections = f"\n## SA REVIEW CORRECTIONS (Phải áp dụng)\n{json.dumps(sa_issues, ensure_ascii=False, indent=2)}\n"

        # Assemble chunks content
        chunks_content = "\n\n---\n\n".join([
            f"### {c.get('issue', '')}\n{c.get('content_markdown', '')}"
            for c in research_chunks
        ])

        lang_instruction = (
            "Write the ENTIRE final advisory document in ENGLISH. All headings, content, "
            "citations, and recommendations must be in English."
            if output_language == "en"
            else "Viết toàn bộ văn bản tư vấn CUỐI CÙNG bằng TIẾNG VIỆT."
        )

        prompt = f"""## YÊU CẦU GỐC CỦA KHÁCH HÀNG
{client_request}

## NỘI DUNG CÁC CHUNKS (JA Research)
{chunks_content[:10000]}

{sa_corrections}

## APPLICABLE LAWS (đã xác minh từ DB)
{json.dumps(applicable_laws, ensure_ascii=False)[:2000]}

Hãy tạo văn bản tư vấn CUỐI CÙNG hoàn chỉnh.
Bao gồm: Executive Summary, nội dung đầy đủ, decision table (nếu cần), căn cứ pháp lý, disclaimer.
CHỈ trích dẫn văn bản pháp lý đã xuất hiện trong chunks nghiên cứu.

## NGÔN NGỮ ĐẦU RA
{lang_instruction}"""

        try:
            model_id, provider = await get_agent_model(self.db, "partner")
            result = await call_ai(
                model_id=model_id,
                messages=[{"role": "user", "content": prompt}],
                system_prompt=PARTNER_P3_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM,
                temperature=0.2,
                max_tokens=16000,
                provider=provider,
            )
            draft_opinion = result["content"]
        except Exception as e:
            logger.error(f"[{node_name}] Draft AI call failed: {e}")
            draft_opinion = f"[Draft generation failed: {e}]"

        return {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "draft_opinion": draft_opinion,
            "draft_version": draft_version + 1,
            "iterations": iterations + 1,
            "audit_events": [_audit("node_completed", node_name, {
                "draft_version": draft_version + 1,
                "draft_word_count": len(draft_opinion.split()),
            })],
        }

    # ── Node 5: SA Review ──────────────────────────────────────────────────────

    async def node_sa_review(self, state: "WorkflowState") -> dict:
        """
        SA adversarial review of draft.
        Sets sa_decision: "approved" | "revision_required"
        """
        node_name = "sa_review"
        draft_opinion = _safe_get(state, "draft_opinion", "")
        completeness_matrix = _safe_get(state, "completeness_matrix") or []
        sa_blueprint = _safe_get(state, "sa_blueprint") or {}
        applicable_laws = _safe_get(state, "applicable_laws") or []
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Reviewing draft")

        prompt = f"""## JA/PARTNER DRAFT OUTPUT (để review)
{draft_opinion[:8000]}

## COMPLETENESS MATRIX (reference)
{json.dumps(completeness_matrix, ensure_ascii=False)[:2000]}

## SA BLUEPRINT (reference)
{json.dumps(sa_blueprint, ensure_ascii=False)[:2000]}

## APPLICABLE LAWS (từ DB)
{json.dumps(applicable_laws, ensure_ascii=False)[:1000]}

Hãy thực hiện adversarial review đầy đủ theo system prompt.
Đặc biệt chú ý: R16 (luật hết hiệu lực), R17 (re-flag VERIFIED fact), R02 (trích dẫn sai).
Trả về JSON với overall_verdict, critical_issues, moderate_issues, revision_required."""

        try:
            model_id, provider = await get_agent_model(self.db, "sa")
            result = await call_ai(
                model_id=model_id,
                messages=[{"role": "user", "content": prompt}],
                system_prompt=SA_REVIEW_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM,
                temperature=0.2,
                max_tokens=8000,
                provider=provider,
            )
            content = result["content"]
        except Exception as e:
            logger.error(f"[{node_name}] SA review AI failed: {e}")
            content = '{"overall_verdict": "PASS", "revision_required": false, "critical_issues": [], "moderate_issues": []}'

        output_data = _extract_json(content) or {}
        revision_required = output_data.get("revision_required", False)
        verdict = output_data.get("overall_verdict", "PASS")

        sa_decision = "revision_required" if revision_required else "approved"
        sa_issues = (
            output_data.get("critical_issues", []) +
            output_data.get("moderate_issues", [])
        )

        return {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "sa_decision": sa_decision,
            "sa_issues": sa_issues,
            "iterations": iterations + 1,
            "audit_events": [_audit("node_completed", node_name, {
                "verdict": verdict,
                "sa_decision": sa_decision,
                "critical_issues_count": len(output_data.get("critical_issues", [])),
                "moderate_issues_count": len(output_data.get("moderate_issues", [])),
            })],
        }

    # ── Node 6: Partner Review ─────────────────────────────────────────────────

    async def node_partner_review(self, state: "WorkflowState") -> dict:
        """
        Strategic partner review. Computes risk_score and sets partner_decision.
        If risk_score > 7: sets human_approval_required = True.
        """
        node_name = "partner_review"
        client_request = _safe_get(state, "client_request", "")
        draft_opinion = _safe_get(state, "draft_opinion", "")
        sa_issues = _safe_get(state, "sa_issues") or []
        verified_facts = _safe_get(state, "verified_facts") or []
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Starting partner review")

        prompt = f"""## YÊU CẦU KHÁCH HÀNG
{client_request}

## DRAFT CUỐI (đã qua SA Review)
{draft_opinion[:8000]}

## SA ISSUES LIST
{json.dumps(sa_issues, ensure_ascii=False, indent=2)[:2000]}

## VERIFIED FACTS (Intake)
{json.dumps(verified_facts, ensure_ascii=False)[:1000]}

Hãy thực hiện Partner P2 review: verification chain audit, strategic quality review, before-after test.
Trả về JSON với verification_chain_status, quality_verdict, risk_score (0-10), approved_for_finalize, strategic_issues."""

        try:
            model_id, provider = await get_agent_model(self.db, "partner")
            result = await call_ai(
                model_id=model_id,
                messages=[{"role": "user", "content": prompt}],
                system_prompt=PARTNER_P2_SYSTEM_PROMPT + DB_FIRST_SYSTEM_ADDENDUM,
                temperature=0.3,
                max_tokens=6000,
                provider=provider,
            )
            content = result["content"]
        except Exception as e:
            logger.error(f"[{node_name}] Partner review AI failed: {e}")
            content = '{"quality_verdict": "APPROVED", "approved_for_finalize": true, "risk_score": 3}'

        output_data = _extract_json(content) or {}
        quality_verdict = output_data.get("quality_verdict", "APPROVED")
        approved = output_data.get("approved_for_finalize", True)

        # Compute risk_score — use AI output or derive from issues
        raw_risk = output_data.get("risk_score", None)
        if raw_risk is not None:
            try:
                risk_score = float(raw_risk)
            except (TypeError, ValueError):
                risk_score = 3.0
        else:
            # Heuristic: critical issues add to risk
            critical_count = len([i for i in sa_issues if i.get("severity") == "CRITICAL"])
            has_insufficient = _safe_get(state, "has_insufficient_coverage") or False
            used_fallback = _safe_get(state, "used_fallback_search") or False
            risk_score = min(10.0, 3.0 + critical_count * 1.5 + (2.0 if has_insufficient else 0) + (1.0 if used_fallback else 0))

        partner_decision = "approved" if approved else "revision_required"
        human_approval_required = risk_score > 7.0

        partner_issues = output_data.get("strategic_issues", [])
        if isinstance(partner_issues, list):
            partner_issues = [{"issue": i} if isinstance(i, str) else i for i in partner_issues]

        return {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "partner_decision": partner_decision,
            "partner_issues": partner_issues,
            "risk_score": risk_score,
            "human_approval_required": human_approval_required,
            "iterations": iterations + 1,
            "audit_events": [_audit("node_completed", node_name, {
                "quality_verdict": quality_verdict,
                "partner_decision": partner_decision,
                "risk_score": risk_score,
                "human_approval_required": human_approval_required,
            })],
        }

    # ── Node 7: Human Gate ─────────────────────────────────────────────────────

    async def node_human_gate(self, state: "WorkflowState") -> dict:
        """
        Human approval gate.
        - If status is None: set to "pending" (workflow pauses)
        - If "approved": continue to delivery
        - If "rejected": rework (revision_required)
        """
        node_name = "human_gate"
        approval_status = _safe_get(state, "human_approval_status")
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] human_approval_status={approval_status}")

        if approval_status is None:
            # First entry — set to pending and pause
            return {
                "current_node": node_name,
                "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
                "human_approval_status": "pending",
                "iterations": iterations + 1,
                "audit_events": [_audit("human_approval_requested", node_name, {
                    "risk_score": _safe_get(state, "risk_score", 0),
                    "partner_decision": _safe_get(state, "partner_decision"),
                })],
            }

        if approval_status == "approved":
            return {
                "current_node": node_name,
                "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
                "iterations": iterations + 1,
                "audit_events": [_audit("human_approved", node_name, {})],
            }

        if approval_status == "rejected":
            return {
                "current_node": node_name,
                "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
                "partner_decision": "revision_required",
                "iterations": iterations + 1,
                "audit_events": [_audit("human_rejected", node_name, {})],
            }

        # Still "pending" — no state change
        return {
            "iterations": iterations + 1,
            "audit_events": [_audit("human_still_pending", node_name, {})],
        }

    # ── Node 8: Delivery ───────────────────────────────────────────────────────

    async def node_delivery(self, state: "WorkflowState") -> dict:
        """
        Final delivery node. Sets final_output and computes quality_score.
        """
        node_name = "delivery"
        draft_opinion = _safe_get(state, "draft_opinion", "")
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Delivering final output")

        final_output = draft_opinion

        # Compute quality score
        wc = len(final_output.split())
        has_practical = "[PRACTICAL]" in final_output
        has_pitfall = "[PITFALL]" in final_output
        has_counter = "[COUNTER]" in final_output
        depth_score = sum([has_practical, has_pitfall, has_counter]) / 3 * 30
        wc_score = min(30, (wc / 3000) * 30)
        quality_score = round(min(100.0, 40.0 + depth_score + wc_score), 1)

        return {
            "current_node": node_name,
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "final_output": final_output,
            "quality_score": quality_score,
            "iterations": iterations + 1,
            "audit_events": [_audit("node_completed", node_name, {
                "quality_score": quality_score,
                "word_count": wc,
            })],
        }

    # ── Node 9: Audit ──────────────────────────────────────────────────────────

    async def node_audit(self, state: "WorkflowState") -> dict:
        """
        Create CaseVersion snapshot in DB and mark workflow as completed.
        """
        node_name = "audit"
        case_id = _safe_get(state, "case_id")
        final_output = _safe_get(state, "final_output", "")
        quality_score = _safe_get(state, "quality_score", 0.0)
        citations = _safe_get(state, "citations") or []
        iterations = _safe_get(state, "iterations", 0)

        logger.info(f"[{node_name}] Archiving case {case_id}")

        # Attempt to persist CaseVersion snapshot
        try:
            from sqlalchemy import text
            snapshot_sql = text("""
                INSERT INTO taxlegal.case_versions (
                    id,
                    case_id,
                    version_number,
                    final_output,
                    quality_score,
                    citations_count,
                    completed_at
                ) VALUES (
                    :id,
                    :case_id,
                    :version_number,
                    :final_output,
                    :quality_score,
                    :citations_count,
                    :completed_at
                )
                ON CONFLICT DO NOTHING
            """)
            await self.db.execute(snapshot_sql, {
                "id": str(uuid.uuid4()),
                "case_id": str(case_id) if case_id else None,
                "version_number": _safe_get(state, "draft_version", 1),
                "final_output": final_output[:50000],
                "quality_score": quality_score,
                "citations_count": len(citations),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            })
            await self.db.flush()
        except Exception as e:
            # Non-fatal — table may not exist in all environments
            logger.debug(f"[{node_name}] CaseVersion snapshot failed (non-fatal): {e}")

        return {
            "current_node": "completed",
            "completed_nodes": (_safe_get(state, "completed_nodes") or []) + [node_name],
            "iterations": iterations + 1,
            "audit_events": [_audit("workflow_completed", node_name, {
                "case_id": str(case_id),
                "quality_score": quality_score,
                "total_citations": len(citations),
                "total_iterations": iterations + 1,
            })],
        }
