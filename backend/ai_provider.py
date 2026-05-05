"""
Unified AI provider abstraction.
Supports: Anthropic, OpenAI, DeepSeek (OpenAI-compat), OpenRouter (OpenAI-compat).
"""
import asyncio
import logging
from typing import Optional
from backend.config import (
    ANTHROPIC_API_KEY, OPENAI_API_KEY,
    DEEPSEEK_API_KEY, OPENROUTER_API_KEY,
)

logger = logging.getLogger(__name__)


def _detect_provider(model_id: str) -> str:
    if "claude" in model_id.lower():
        return "anthropic"
    if model_id.startswith(("gpt-", "o1", "o3", "o4")):
        return "openai"
    if "deepseek" in model_id.lower():
        return "deepseek"
    # Anything with a slash (e.g. "qwen/qwen3-72b") is OpenRouter
    if "/" in model_id:
        return "openrouter"
    return "openai"


async def call_ai(
    model_id: str,
    messages: list[dict],
    system_prompt: str = "",
    temperature: float = 0.3,
    max_tokens: int = 8000,
    provider: Optional[str] = None,
) -> dict:
    """
    Call an AI model and return {"content": str, "prompt_tokens": int, "completion_tokens": int}.
    """
    if provider is None:
        provider = _detect_provider(model_id)

    try:
        if provider == "anthropic":
            return await _call_anthropic(model_id, messages, system_prompt, temperature, max_tokens)
        elif provider == "openai":
            return await _call_openai(model_id, messages, system_prompt, temperature, max_tokens)
        elif provider == "deepseek":
            return await _call_deepseek(model_id, messages, system_prompt, temperature, max_tokens)
        elif provider == "openrouter":
            return await _call_openrouter(model_id, messages, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    except Exception as e:
        logger.error(f"AI call failed [{provider}/{model_id}]: {e}")
        raise


# ── Anthropic ─────────────────────────────────────────────────────────────────

async def _call_anthropic(model_id, messages, system_prompt, temperature, max_tokens) -> dict:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    kwargs = dict(
        model=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=messages,
    )
    if system_prompt:
        kwargs["system"] = system_prompt
    resp = await client.messages.create(**kwargs)
    return {
        "content": resp.content[0].text,
        "prompt_tokens": resp.usage.input_tokens,
        "completion_tokens": resp.usage.output_tokens,
    }


# ── OpenAI ────────────────────────────────────────────────────────────────────

async def _call_openai(model_id, messages, system_prompt, temperature, max_tokens) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)
    resp = await client.chat.completions.create(
        model=model_id,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "content": resp.choices[0].message.content,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
    }


# ── DeepSeek ─────────────────────────────────────────────────────────────────

async def _call_deepseek(model_id, messages, system_prompt, temperature, max_tokens) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)
    resp = await client.chat.completions.create(
        model=model_id,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "content": resp.choices[0].message.content,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
    }


# ── OpenRouter ────────────────────────────────────────────────────────────────

async def _call_openrouter(model_id, messages, system_prompt, temperature, max_tokens) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://taxlegal.app",
            "X-Title": "TaxLegal AI",
        },
    )
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)
    resp = await client.chat.completions.create(
        model=model_id,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "content": resp.choices[0].message.content,
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
