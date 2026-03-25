from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI
from tenacity import retry, wait_exponential, stop_after_attempt


def _client_from_env() -> OpenAI | None:
    # Support multiple providers without changing call sites.
    #
    # 1) OpenAI (default)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return OpenAI(api_key=openai_key)

    # 2) Groq (OpenAI-compatible)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
        return OpenAI(api_key=groq_key, base_url=base_url)

    return None


@retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
def chat_completion_json(model: str, system: str, user: str) -> dict[str, Any]:
    """
    Returns a parsed JSON object. If JSON parsing fails, raises.
    """
    client = _client_from_env()
    if client is None:
        raise RuntimeError("No LLM provider key set (OPENAI_API_KEY or GROQ_API_KEY)")

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=900,
    )
    text = resp.choices[0].message.content or ""
    return json.loads(text)


def best_effort_chat_completion_json(model: str, system: str, user: str) -> dict[str, Any] | None:
    """
    Non-fatal wrapper: returns None if LLM is unavailable or JSON can't be parsed.
    """
    try:
        return chat_completion_json(model=model, system=system, user=user)
    except Exception:
        return None


@retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
def chat_completion_text(model: str, system: str, user: str) -> str:
    client = _client_from_env()
    if client is None:
        raise RuntimeError("No LLM provider key set (OPENAI_API_KEY or GROQ_API_KEY)")

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
        max_tokens=550,
    )
    return resp.choices[0].message.content or ""


def best_effort_chat_completion_text(model: str, system: str, user: str) -> str | None:
    """
    Non-fatal wrapper: returns None if LLM is unavailable or errors.
    """
    try:
        return chat_completion_text(model=model, system=system, user=user).strip()
    except Exception:
        return None

