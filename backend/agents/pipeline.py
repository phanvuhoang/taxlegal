"""
Pipeline Engine — orchestrates 7-step agent pipeline.
Each step runs sequentially, saves to DB, then waits for approval (manual mode)
or continues automatically (auto mode).
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.models import Matter, PipelineStep, ResearchChunk, MatterStatus, BotVariant, PipelineTemplate, Skill
from backend.ai_provider import call_ai
from backend.web_search import (
    verify_fact, verify_law_currency, search_practical_guidance, web_search
)
from backend.agents.prompts import (
    INTAKE_SYSTEM_PROMPT, PARTNER_P1_SYSTEM_PROMPT, SA_BLUEPRINT_SYSTEM_PROMPT,
    JA_RESEARCH_SYSTEM_PROMPT, SA_REVIEW_SYSTEM_PROMPT,
    PARTNER_P2_SYSTEM_PROMPT, PARTNER_P3_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

STEP_MAP = {
    1: {"name": "intake", "agent": "intake", "status": MatterStatus.intake},
    2: {"name": "partner_p1", "agent": "partner", "status": MatterStatus.partner_p1},
    3: {"name": "sa_blueprint", "agent": "sa", "status": MatterStatus.sa_blueprint},
    4: {"name": "ja_research", "agent": "ja", "status": MatterStatus.ja_research},
    5: {"name": "sa_review", "agent": "sa", "status": MatterStatus.sa_review},
    6: {"name": "partner_p2", "agent": "partner", "status": MatterStatus.partner_p2},
    7: {"name": "partner_p3", "agent": "partner", "status": MatterStatus.partner_p3},
}


async def get_agent_model(db: AsyncSession, agent_key: str) -> tuple[str, str]:
    """Return (model_id, provider) for agent from DB settings."""
    from backend.models import AgentSetting
    result = await db.execute(
        select(AgentSetting).where(AgentSetting.agent_key == agent_key)
    )
    setting = result.scalar_one_or_none()
    if setting:
        return setting.model_id, setting.provider
    from backend.config import DEFAULT_AGENT_MODELS
    model_id = DEFAULT_AGENT_MODELS.get(agent_key, "gpt-4o")
    provider = "anthropic" if "claude" in model_id else "openai"
    return model_id, provider


async def build_step_input(db: AsyncSession, matter: Matter, step_number: int) -> dict:
    """Build input dict for a step by reading previous step outputs."""
    result = await db.execute(
        select(PipelineStep)
        .where(PipelineStep.matter_id == matter.id)
        .order_by(PipelineStep.step_number)
    )
    steps = result.scalars().all()
    step_outputs = {s.step_number: s.output_data for s in steps if s.output_data}

    return {
        "client_request": matter.client_request,
        "title": matter.title,
        "practice_area": matter.practice_area,
        "output_language": getattr(matter, "output_language", "vi"),
        "step_number": step_number,
        "previous_steps": step_outputs,
        "verified_facts": matter.verified_facts or [],
        "applicable_laws": matter.applicable_laws or [],
        "completeness_matrix": matter.completeness_matrix or [],
        "partner_brief": matter.partner_brief,
        "sa_blueprint": matter.sa_blueprint,
        "word_count_floor": matter.word_count_floor or 3000,
    }


async def run_intake_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 1: Intake Enhancer"""
    # First, do preliminary web searches for fact/law verification
    searches = []
    # Search for applicable laws
    law_search = await web_search(
        f"Luật Việt Nam áp dụng cho: {matter.client_request[:200]} — văn bản pháp lý hiện hành 2024 2025",
        context="legal research Vietnam"
    )
    searches.append({"query": "applicable laws", "result": law_search})

    prompt = f"""## YÊU CẦU CỦA KHÁCH HÀNG
{matter.client_request}

## KẾT QUẢ TÌM KIẾM WEB BAN ĐẦU
{json.dumps(law_search, ensure_ascii=False, indent=2)}

Hãy phân tích và tạo Enriched Request theo đúng format JSON đã được định nghĩa trong system prompt.
Tập trung vào việc xác minh sự kiện, kiểm tra hiệu lực luật, và xây dựng completeness matrix đầy đủ."""

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": prompt}],
        system_prompt=await build_system_prompt_with_skills(db, INTAKE_SYSTEM_PROMPT, bot_variant),
        temperature=0.2,
        max_tokens=8000,
        provider=provider,
    )

    # Parse JSON from response
    content = result["content"]
    output_data = _extract_json_from_response(content)

    # Update matter with intake data
    if output_data:
        matter.verified_facts = output_data.get("verified_facts", [])
        matter.applicable_laws = output_data.get("applicable_laws", [])
        matter.completeness_matrix = output_data.get("completeness_matrix", [])
        matter.word_count_floor = output_data.get("word_count_floor", 3000)

    return {
        "output_data": output_data,
        "output_markdown": content,
        "search_queries": searches,
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }


async def run_partner_p1_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 2: Partner P1 Brief"""
    intake_data = json.dumps({
        "verified_facts": matter.verified_facts,
        "applicable_laws": matter.applicable_laws,
        "completeness_matrix": matter.completeness_matrix,
        "word_count_floor": matter.word_count_floor,
    }, ensure_ascii=False, indent=2)

    prompt = f"""## YÊU CẦU GỐC CỦA KHÁCH HÀNG
{matter.client_request}

## ENRICHED REQUEST (TỪ INTAKE ENHANCER)
{intake_data}

Hãy tạo Partner Brief theo đúng format JSON trong system prompt.
Đây là "lệnh điều quân" — phải đủ cụ thể để SA và JA không cần hỏi lại."""

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": prompt}],
        system_prompt=await build_system_prompt_with_skills(db, PARTNER_P1_SYSTEM_PROMPT, bot_variant),
        temperature=0.3,
        max_tokens=6000,
        provider=provider,
    )

    content = result["content"]
    output_data = _extract_json_from_response(content)
    if output_data:
        matter.partner_brief = output_data

    return {
        "output_data": output_data,
        "output_markdown": content,
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }


async def run_sa_blueprint_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 3: SA Blueprint"""
    context = json.dumps({
        "verified_facts": matter.verified_facts,
        "applicable_laws": matter.applicable_laws,
        "completeness_matrix": matter.completeness_matrix,
        "partner_brief": matter.partner_brief,
    }, ensure_ascii=False, indent=2)

    prompt = f"""## YÊU CẦU KHÁCH HÀNG
{matter.client_request}

## CONTEXT (Intake + Partner Brief)
{context}

Hãy thiết kế Document Blueprint và Chunk Division theo format JSON trong system prompt.
Đảm bảo thứ tự theo CLIENT-READING ORDER và Deduplication Map rõ ràng."""

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": prompt}],
        system_prompt=await build_system_prompt_with_skills(db, SA_BLUEPRINT_SYSTEM_PROMPT, bot_variant),
        temperature=0.2,
        max_tokens=8000,
        provider=provider,
    )

    content = result["content"]
    output_data = _extract_json_from_response(content)
    if output_data:
        matter.sa_blueprint = output_data

    return {
        "output_data": output_data,
        "output_markdown": content,
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }


async def run_ja_research_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 4: JA Research — process all chunks"""
    blueprint = matter.sa_blueprint or {}
    chunks = blueprint.get("chunks", [])

    if not chunks:
        # Fallback: create a single chunk from completeness matrix
        chunks = [
            {
                "chunk_id": i + 1,
                "section": f"Phần {i+1}",
                "issue": item.get("issue", f"Vấn đề {i+1}"),
                "depth": item.get("depth", "STANDARD"),
                "word_count_target": 600,
            }
            for i, item in enumerate(matter.completeness_matrix or [{"issue": matter.client_request[:100]}])
        ]

    all_chunks_markdown = []
    all_chunks_data = []
    total_prompt_tokens = 0
    total_completion_tokens = 0
    search_queries = []

    for chunk_def in chunks[:10]:  # cap at 10 chunks per matter
        chunk_issue = chunk_def.get("issue", "")
        chunk_depth = chunk_def.get("depth", "STANDARD")
        chunk_id = chunk_def.get("chunk_id", 1)

        # Web searches for this chunk
        practical_search = await search_practical_guidance(chunk_issue, "luật Việt Nam")
        search_queries.append({"chunk": chunk_id, "type": "practical", "query": chunk_issue})

        # Legal verification for laws mentioned in applicable_laws
        law_verifications = []
        for law in (matter.applicable_laws or [])[:3]:
            vr = await verify_law_currency(law.get("so_hieu", ""), "")
            law_verifications.append(vr)

        chunk_prompt = f"""## CHUNK CẦN NGHIÊN CỨU
Chunk ID: {chunk_id}
Vấn đề: {chunk_issue}
Độ sâu: {chunk_depth}
Word count target: {chunk_def.get("word_count_target", 600)} từ

## CONTEXT
Yêu cầu khách hàng: {matter.client_request[:500]}
Verified facts: {json.dumps(matter.verified_facts or [], ensure_ascii=False)}
Partner brief guidance: {json.dumps(matter.partner_brief or {}, ensure_ascii=False)[:1000]}

## KẾT QUẢ TÌM KIẾM THỰC TIỄN
{json.dumps(practical_search, ensure_ascii=False, indent=2)[:2000]}

## LUẬT ĐÃ XÁC MINH HIỆU LỰC
{json.dumps(law_verifications, ensure_ascii=False, indent=2)[:2000]}

Hãy thực hiện đầy đủ 5 phases (A, B1, B2, B2.5, C) và tạo:
1. JSON nghiên cứu (phase outputs)
2. Văn bản tư vấn Markdown cho chunk này"""

        result = await call_ai(
            model_id=model_id,
            messages=[{"role": "user", "content": chunk_prompt}],
            system_prompt=await build_system_prompt_with_skills(db, JA_RESEARCH_SYSTEM_PROMPT, bot_variant),
            temperature=0.3,
            max_tokens=8000,
            provider=provider,
        )

        chunk_content = result["content"]
        chunk_data = _extract_json_from_response(chunk_content)
        total_prompt_tokens += result["prompt_tokens"]
        total_completion_tokens += result["completion_tokens"]
        all_chunks_markdown.append(f"\n\n---\n\n{chunk_content}")
        all_chunks_data.append({"chunk_id": chunk_id, "data": chunk_data})

        # Save chunk to DB
        db_chunk = ResearchChunk(
            matter_id=matter.id,
            chunk_number=chunk_id,
            section_title=chunk_issue,
            depth_level=chunk_depth,
            content_markdown=chunk_content,
            evidence_collected=chunk_data.get("phase_a_evidence", []) if chunk_data else [],
            practical_research=chunk_data.get("phase_b1_practical", []) if chunk_data else [],
            legal_verification=chunk_data.get("phase_b2_legal_verification", []) if chunk_data else [],
            assertion_verification=chunk_data.get("phase_b25_assertion_verification", []) if chunk_data else [],
            depth_markers=chunk_data.get("depth_markers_used", []) if chunk_data else [],
            depth_marker_count=len(chunk_data.get("depth_markers_used", [])) if chunk_data else 0,
        )
        db.add(db_chunk)

    await db.flush()

    return {
        "output_data": {"chunks": all_chunks_data},
        "output_markdown": "\n".join(all_chunks_markdown),
        "search_queries": search_queries,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
    }


async def run_sa_review_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 5: SA Adversarial Review"""
    # Get JA output (step 4)
    result_q = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter.id,
            PipelineStep.step_number == 4
        )
    )
    ja_step = result_q.scalar_one_or_none()
    ja_content = (ja_step.output_markdown or "")[:8000] if ja_step else ""

    # Independent web searches for verification
    spot_checks = []
    for law in (matter.applicable_laws or [])[:3]:
        vc = await verify_law_currency(law.get("so_hieu", ""), "")
        spot_checks.append(vc)

    prompt = f"""## JA RESEARCH OUTPUT (để review)
{ja_content}

## COMPLETENESS MATRIX (reference)
{json.dumps(matter.completeness_matrix or [], ensure_ascii=False)}

## SA BLUEPRINT (reference)
{json.dumps(matter.sa_blueprint or {}, ensure_ascii=False)[:2000]}

## INDEPENDENT LAW VERIFICATIONS (SA tự search — không tin JA)
{json.dumps(spot_checks, ensure_ascii=False, indent=2)}

Hãy thực hiện adversarial review đầy đủ theo system prompt.
Đặc biệt chú ý: R16 (luật hết hiệu lực), R17 (re-flag VERIFIED fact), R02 (trích dẫn sai)."""

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": prompt}],
        system_prompt=await build_system_prompt_with_skills(db, SA_REVIEW_SYSTEM_PROMPT, bot_variant),
        temperature=0.2,
        max_tokens=8000,
        provider=provider,
    )

    content = result["content"]
    output_data = _extract_json_from_response(content)

    # Extract reason codes
    reason_codes = []
    if output_data:
        for issue in output_data.get("critical_issues", []):
            reason_codes.append({
                "code": issue.get("code"),
                "severity": "CRITICAL",
                "step": "sa_review",
                "detail": issue.get("description", ""),
            })
        for issue in output_data.get("moderate_issues", []):
            reason_codes.append({
                "code": issue.get("code"),
                "severity": "MODERATE",
                "step": "sa_review",
                "detail": issue.get("description", ""),
            })
        # Merge into matter reason_codes
        existing = matter.reason_codes or []
        matter.reason_codes = existing + reason_codes

    return {
        "output_data": output_data,
        "output_markdown": content,
        "reason_codes_found": reason_codes,
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }


async def run_partner_p2_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 6: Partner P2 — Strategic Review"""
    result_q = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter.id,
            PipelineStep.step_number.in_([4, 5])
        )
    )
    prev_steps = result_q.scalars().all()
    prev_content = "\n\n---\n\n".join([
        f"## Step {s.step_number} ({s.step_name})\n{(s.output_markdown or '')[:3000]}"
        for s in prev_steps
    ])

    prompt = f"""## YÊU CẦU KHÁCH HÀNG
{matter.client_request}

## JA + SA OUTPUTS
{prev_content[:8000]}

## VERIFIED FACTS (Intake)
{json.dumps(matter.verified_facts or [], ensure_ascii=False)}

Hãy thực hiện Partner P2 review theo system prompt: verification chain audit, strategic quality review, before-after test."""

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": prompt}],
        system_prompt=await build_system_prompt_with_skills(db, PARTNER_P2_SYSTEM_PROMPT, bot_variant),
        temperature=0.3,
        max_tokens=6000,
        provider=provider,
    )

    content = result["content"]
    output_data = _extract_json_from_response(content)
    if output_data:
        matter.verification_chain_status = output_data.get("verification_chain_status")

    return {
        "output_data": output_data,
        "output_markdown": content,
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }


async def run_partner_p3_step(db: AsyncSession, matter: Matter, step: PipelineStep, model_id: str, provider: str, bot_variant=None):
    """Step 7: Partner P3 — Finalize"""
    # Collect all JA chunks
    chunks_q = await db.execute(
        select(ResearchChunk)
        .where(ResearchChunk.matter_id == matter.id)
        .order_by(ResearchChunk.chunk_number)
    )
    chunks = chunks_q.scalars().all()
    chunks_content = "\n\n---\n\n".join([
        f"### {c.section_title}\n{c.content_markdown or ''}"
        for c in chunks
    ])

    # SA corrections
    sa_q = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter.id,
            PipelineStep.step_number == 5
        )
    )
    sa_step = sa_q.scalar_one_or_none()
    sa_content = (sa_step.output_markdown or "")[:3000] if sa_step else ""

    # Partner P2 instructions
    p2_q = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter.id,
            PipelineStep.step_number == 6
        )
    )
    p2_step = p2_q.scalar_one_or_none()
    p2_content = (p2_step.output_markdown or "")[:2000] if p2_step else ""

    prompt = f"""## YÊU CẦU GỐC CỦA KHÁCH HÀNG
{matter.client_request}

## NỘI DUNG CÁC CHUNKS (JA Research)
{chunks_content[:10000]}

## SA REVIEW CORRECTIONS
{sa_content}

## PARTNER P2 FINALIZE INSTRUCTIONS
{p2_content}

## APPLICABLE LAWS (đã xác minh)
{json.dumps(matter.applicable_laws or [], ensure_ascii=False)}

Hãy tạo văn bản tư vấn CUỐI CÙNG hoàn chỉnh theo system prompt. 
Bao gồm: Executive Summary, nội dung đầy đủ, decision table (nếu cần), căn cứ pháp lý, disclaimer.

## NGÔN NGỮ ĐẦU RA
{"Write the ENTIRE final advisory document in ENGLISH. All headings, content, citations, and recommendations must be in English." if getattr(matter, 'output_language', 'vi') == 'en' else "Viết toàn bộ văn bản tư vấn CUỐI CÙNG bằng TIẾNG VIỆT. Tất cả các mục, nội dung, trích dẫn và khuyến nghị phải bằng tiếng Việt."}"""

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": prompt}],
        system_prompt=await build_system_prompt_with_skills(db, PARTNER_P3_SYSTEM_PROMPT, bot_variant),
        temperature=0.2,
        max_tokens=16000,
        provider=provider,
    )

    content = result["content"]
    matter.final_content = content

    # Estimate quality score
    wc = len(content.split())
    has_practical = "[PRACTICAL]" in content
    has_pitfall = "[PITFALL]" in content
    has_counter = "[COUNTER]" in content
    depth_score = sum([has_practical, has_pitfall, has_counter]) / 3 * 30
    wc_score = min(30, (wc / max(matter.word_count_floor or 3000, 1)) * 30)
    base_score = 40 + depth_score + wc_score
    matter.quality_score = round(min(100, base_score), 1)

    return {
        "output_data": {"word_count": wc, "quality_score": matter.quality_score},
        "output_markdown": content,
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }


async def execute_pipeline_step(
    db: AsyncSession,
    matter_id: int,
    step_number: int,
    model_override: Optional[str] = None,
) -> PipelineStep:
    """
    Execute one pipeline step. Updates step status and matter status.
    Returns the completed PipelineStep.
    """
    # Load matter
    matter_result = await db.execute(select(Matter).where(Matter.id == matter_id))
    matter = matter_result.scalar_one_or_none()
    if not matter:
        raise ValueError(f"Matter {matter_id} not found")

    step_info = STEP_MAP.get(step_number)
    if not step_info:
        raise ValueError(f"Invalid step number: {step_number}")

    agent_key = step_info["agent"]

    # Get or create step record
    step_result = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter_id,
            PipelineStep.step_number == step_number
        )
    )
    step = step_result.scalar_one_or_none()
    if not step:
        step = PipelineStep(
            matter_id=matter_id,
            step_number=step_number,
            step_name=step_info["name"],
            agent=agent_key,
        )
        db.add(step)
        await db.flush()

    # Get BotVariant for this step (may override model and system prompt)
    bot_variant = await get_bot_for_step(db, matter, step_number)

    # Get model
    if model_override:
        from backend.ai_provider import _detect_provider
        model_id = model_override
        provider = _detect_provider(model_id)
    elif bot_variant and bot_variant.model_override:
        model_id = bot_variant.model_override
        if bot_variant.provider_override:
            provider = bot_variant.provider_override
        else:
            from backend.ai_provider import _detect_provider
            provider = _detect_provider(model_id)
    else:
        model_id, provider = await get_agent_model(db, agent_key)

    step.status = "running"
    step.model_used = model_id
    step.provider_used = provider
    step.started_at = datetime.utcnow()
    matter.current_step = step_number
    matter.status = step_info["status"].value
    await db.flush()

    try:
        # Dispatch to correct step function
        runners = {
            1: run_intake_step,
            2: run_partner_p1_step,
            3: run_sa_blueprint_step,
            4: run_ja_research_step,
            5: run_sa_review_step,
            6: run_partner_p2_step,
            7: run_partner_p3_step,
        }
        runner = runners[step_number]
        output = await runner(db, matter, step, model_id, provider, bot_variant=bot_variant)

        # Update step
        step.output_data = output.get("output_data")
        step.output_markdown = output.get("output_markdown", "")
        step.search_queries = output.get("search_queries", [])
        step.reason_codes_found = output.get("reason_codes_found", [])
        step.prompt_tokens = output.get("prompt_tokens", 0)
        step.completion_tokens = output.get("completion_tokens", 0)
        step.completed_at = datetime.utcnow()
        step.duration_ms = int((step.completed_at - step.started_at).total_seconds() * 1000)

        # Word count
        wc = len((step.output_markdown or "").split())
        step.word_count = wc

        # Update matter model tracking
        model_field = f"model_used_{agent_key}"
        if hasattr(matter, model_field):
            setattr(matter, model_field, model_id)
        matter.total_tokens = (matter.total_tokens or 0) + step.prompt_tokens + step.completion_tokens

        if step_number == 7:
            # Final step
            matter.status = MatterStatus.completed.value
            step.status = "completed"
        else:
            step.status = "waiting"  # wait for user approval

        await db.commit()
        return step

    except Exception as e:
        logger.error(f"Pipeline step {step_number} failed for matter {matter_id}: {e}")
        step.status = "failed"
        step.error_message = str(e)
        matter.status = MatterStatus.failed.value
        await db.commit()
        raise


def _extract_json_from_response(text: str) -> Optional[dict]:
    """Extract JSON from AI response (handles markdown code blocks)."""
    import re
    # Try ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Try bare JSON
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    return None


async def approve_step_and_continue(
    db: AsyncSession,
    matter_id: int,
    step_number: int,
    user_id: int,
    notes: str = "",
    model_override: Optional[str] = None,
) -> Optional[PipelineStep]:
    """Approve current step and optionally trigger next step (for auto mode)."""
    # Mark step approved
    result = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter_id,
            PipelineStep.step_number == step_number,
        )
    )
    step = result.scalar_one_or_none()
    if not step:
        raise ValueError(f"Step {step_number} not found")
    step.status = "approved"
    step.user_notes = notes
    step.approved_at = datetime.utcnow()
    step.approved_by = user_id
    await db.commit()

    # Check if there's a next step
    next_step = step_number + 1
    if next_step <= 7:
        return await execute_pipeline_step(db, matter_id, next_step, model_override)
    return None


# ── Skills + BotVariants integration ──────────────────────────────────────────

async def get_bot_for_step(
    db: AsyncSession,
    matter: "Matter",
    step_number: int,
) -> "Optional[BotVariant]":
    """
    Return the BotVariant for a given step, considering:
    1. matter.bot_variant_overrides (per-matter override map {step: bot_variant_slug})
    2. The matter's PipelineTemplate step_config
    3. The default PipelineTemplate's step_config
    Falls back to None if no BotVariant slug is found (use system defaults).
    """
    slug: Optional[str] = None

    # 1. Per-matter overrides take highest priority
    overrides = matter.bot_variant_overrides or {}
    slug = overrides.get(str(step_number))

    if not slug:
        # 2. Look up the matter's pipeline template (or the default)
        template_id = getattr(matter, "pipeline_template_id", None)
        template: Optional[PipelineTemplate] = None

        if template_id:
            result = await db.execute(
                select(PipelineTemplate).where(PipelineTemplate.id == template_id)
            )
            template = result.scalar_one_or_none()

        if not template:
            # Fall back to the default template
            result = await db.execute(
                select(PipelineTemplate).where(
                    PipelineTemplate.is_default == True,
                    PipelineTemplate.is_active == True,
                )
            )
            template = result.scalar_one_or_none()

        if template and template.step_config:
            step_cfg = template.step_config.get(str(step_number)) or {}
            slug = step_cfg.get("bot_variant_slug")

    if not slug:
        return None

    # Resolve slug to BotVariant
    result = await db.execute(
        select(BotVariant).where(
            BotVariant.slug == slug,
            BotVariant.is_active == True,
        )
    )
    return result.scalar_one_or_none()


async def build_system_prompt_with_skills(
    db: AsyncSession,
    base_prompt: str,
    bot_variant: "Optional[BotVariant]",
) -> str:
    """
    Enrich base_prompt with skill content injected from the BotVariant's skill_ids.
    If bot_variant is None or has no skill_ids, returns base_prompt unchanged.
    If bot_variant has a system_prompt_base set, that overrides base_prompt before
    skill injection.
    """
    if bot_variant is None:
        return base_prompt

    # Use variant's system_prompt_base if provided
    effective_prompt = bot_variant.system_prompt_base or base_prompt

    skill_ids = bot_variant.skill_ids or []
    if not skill_ids:
        return effective_prompt

    # Load skills
    result = await db.execute(
        select(Skill).where(
            Skill.id.in_(skill_ids),
            Skill.is_active == True,
        )
    )
    skills = result.scalars().all()
    if not skills:
        return effective_prompt

    # Append skill content
    skills_section = "\n\n---\n## SKILLS ACTIVATED\n"
    for skill in skills:
        skills_section += f"\n### {skill.name}\n{skill.content_markdown}\n"

    return effective_prompt + skills_section
