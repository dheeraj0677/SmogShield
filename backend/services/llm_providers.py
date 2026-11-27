"""Provider helpers for OpenRouter free models and Google Gemini API."""

import asyncio
import logging

import httpx
from google import genai
from google.genai import types

from config import Settings
from services.prompt_builder import SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

OPENROUTER_FREE_FALLBACKS = (
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "openrouter/free",
    "nvidia/nemotron-3.5-lightning:free",
)


def resolve_free_openrouter_model(model_id: str) -> str:
    """Enforce free-tier-only OpenRouter models (:free suffix or openrouter/free)."""
    cleaned = (model_id or "").strip()
    if cleaned == "openrouter/free" or cleaned.endswith(":free"):
        return cleaned
    logger.warning(
        "Non-free OpenRouter model '%s' blocked by free-models-only policy; "
        "using openrouter/free.",
        cleaned,
    )
    return "openrouter/free"


async def call_openrouter_api(
    settings: Settings,
    enriched_prompt: str,
    client: httpx.AsyncClient | None = None,
) -> tuple[str | None, str]:
    """Invoke OpenRouter free-tier chat completions API with multi-model fallback."""
    primary = resolve_free_openrouter_model(settings.openrouter_model)
    candidates = [primary] + [m for m in OPENROUTER_FREE_FALLBACKS if m != primary]
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "SmogShield Urban Air Quality Assistant",
    }

    close_client = client is None
    http_client = client or httpx.AsyncClient(timeout=settings.request_timeout_seconds)
    try:
        for model_id in candidates:
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": enriched_prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 700,
            }
            try:
                resp = await http_client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code != 200:
                    logger.warning(
                        "OpenRouter free model %s returned HTTP %s", model_id, resp.status_code
                    )
                    continue
                data = resp.json()
                choices = data.get("choices") or []
                msg = (choices[0].get("message") or {}) if choices else {}
                raw_content = msg.get("content")
                content = raw_content.strip() if isinstance(raw_content, str) else ""
                if content:
                    return content, str(data.get("model") or model_id)
            except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
                logger.warning("OpenRouter call failed for %s: %s", model_id, exc)
        return None, primary
    finally:
        if close_client:
            await http_client.aclose()


async def call_gemini_api(settings: Settings, enriched_prompt: str) -> str | None:
    """Invoke Google Gemini API safely with timeout and graceful fallback."""

    def _sync_invoke() -> str:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=enriched_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.4,
                max_output_tokens=700,
            ),
        )
        return (response.text or "").strip()

    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(_sync_invoke),
            timeout=settings.request_timeout_seconds,
        )
        return text if text else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini invocation failed; using structured fallback: %s", exc)
        return None
