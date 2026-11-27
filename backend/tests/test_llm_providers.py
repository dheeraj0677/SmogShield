"""Tests for OpenRouter free-model provider and Gemini SDK invocation."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from config import Settings
from services.llm_providers import (
    call_gemini_api,
    call_openrouter_api,
    resolve_free_openrouter_model,
)


def test_resolve_free_openrouter_model_enforces_free_tier():
    assert resolve_free_openrouter_model("google/gemma-4-26b-a4b-it:free").endswith(":free")
    assert resolve_free_openrouter_model("openrouter/free") == "openrouter/free"
    assert resolve_free_openrouter_model("openai/gpt-4o") == "openrouter/free"
    assert resolve_free_openrouter_model("") == "openrouter/free"


@pytest.mark.asyncio
async def test_call_openrouter_api_success_and_fallbacks():
    settings = Settings(
        openrouter_api_key="sk-or-v1-test",
        openrouter_model="google/gemma-4-26b-a4b-it:free",
    )
    client = AsyncMock(spec=httpx.AsyncClient)

    ok_resp = MagicMock()
    ok_resp.status_code = 200
    ok_resp.json.return_value = {
        "model": "google/gemma-4-26b-a4b-it:free",
        "choices": [{"message": {"content": "Wear an N95 mask today."}}],
    }
    client.post.return_value = ok_resp
    text, model = await call_openrouter_api(settings, "hello", client=client)
    assert text == "Wear an N95 mask today."
    assert model == "google/gemma-4-26b-a4b-it:free"

    # 429 then null content then HTTP error -> returns (None, primary)
    rate_resp = MagicMock(status_code=429)
    null_resp = MagicMock(status_code=200)
    null_resp.json.return_value = {"choices": [{"message": {"content": None}}]}
    client.post.side_effect = [
        rate_resp,
        null_resp,
        httpx.ReadTimeout("timeout"),
        rate_resp,
        rate_resp,
    ]
    text, model = await call_openrouter_api(settings, "hello", client=client)
    assert text is None
    assert model == "google/gemma-4-26b-a4b-it:free"


@pytest.mark.asyncio
async def test_call_gemini_api_handles_success_and_error():
    settings = Settings(gemini_api_key="test-gemini-key", gemini_model="gemini-2.5-flash")
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text="  Stay indoors.  ")

    with patch("services.llm_providers.genai.Client", return_value=mock_client):
        result = await call_gemini_api(settings, "Test prompt")
    assert result == "Stay indoors."

    mock_client.models.generate_content.side_effect = RuntimeError("quota exceeded")
    with patch("services.llm_providers.genai.Client", return_value=mock_client):
        result = await call_gemini_api(settings, "Test prompt")
    assert result is None
