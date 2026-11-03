"""NVIDIA NIM access: CrewAI LLM factory + direct OpenAI-compatible client.

The hosted endpoint (https://integrate.api.nvidia.com/v1) is OpenAI-compatible,
so CrewAI talks to it through LiteLLM's `openai/` prefix with a custom base_url,
and non-CrewAI code (validation, JSON repair) uses the `openai` SDK directly.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# Disable nonessential OpenTelemetry export before CrewAI / LiteLLM imports
# (same convention as the Portfolio-Agent crew modules).
os.environ.setdefault("OTEL_SDK_DISABLED", "true")


def litellm_model_string() -> str:
    """LiteLLM model id: openai/ prefix + custom base_url = NIM endpoint."""
    return f"openai/{settings.nim_model}"


def crewai_llm(temperature: float = 0.2, timeout: int = 240, max_tokens: int = 8192):
    """CrewAI LLM pointed at NVIDIA NIM."""
    if not settings.has_nvidia:
        raise RuntimeError("NVIDIA_API_KEY is not configured (add it to .env)")
    from crewai import LLM

    return LLM(
        model=litellm_model_string(),
        base_url=settings.nim_base_url,
        api_key=settings.nvidia_api_key,
        temperature=temperature,
        timeout=timeout,
        max_tokens=max_tokens,
    )


def direct_client():
    """Plain OpenAI SDK client for non-CrewAI calls (connectivity checks, JSON repair)."""
    from openai import OpenAI

    if not settings.has_nvidia:
        raise RuntimeError("NVIDIA_API_KEY is not configured (add it to .env)")
    return OpenAI(base_url=settings.nim_base_url, api_key=settings.nvidia_api_key)


def check_nim() -> dict[str, Any]:
    """Minimal connectivity probe used by /api/health and setup verification."""
    if not settings.has_nvidia:
        return {"ok": False, "error": "NVIDIA_API_KEY not configured"}
    try:
        client = direct_client()
        model_ids = [m.id for m in client.models.list().data]
        configured = settings.nim_model in model_ids
        return {
            "ok": True,
            "base_url": settings.nim_base_url,
            "model": settings.nim_model,
            "model_listed": configured,
            "available_nemotron": [m for m in model_ids if "nemotron" in m.lower()][:8],
        }
    except Exception as exc:  # noqa: BLE001 - report any probe failure verbatim
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
