"""Tests for OpenRouter free-model enforcement and null-content fallback."""

import json

import httpx
from fastapi.testclient import TestClient

from config import Settings
from main import create_app
from services.gemini_service import GeminiService, resolve_free_openrouter_model
from tests.conftest import make_snapshot


def test_openrouter_enforces_free_models_only_and_handles_chat():
    assert resolve_free_openrouter_model("openai/gpt-4o") == "openrouter/free"
    assert (
        resolve_free_openrouter_model("google/gemma-4-26b-a4b-it:free")
        == "google/gemma-4-26b-a4b-it:free"
    )

    or_settings = Settings(
        openrouter_api_key="sk-or-test-key",
        openrouter_model="openai/gpt-4o",
        gemini_api_key="",
        app_env="test",
    )
    custom_app = create_app(settings=or_settings)

    async def mock_aqi(city: str):
        return make_snapshot(city=city, aqi=215)

    captured_models: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        captured_models.append(body["model"])
        return httpx.Response(
            200,
            json={
                "model": "google/gemma-4-26b-a4b-it:free",
                "choices": [
                    {
                        "message": {
                            "content": "At AQI 215, use a snug N95 mask and run a HEPA filter."
                        }
                    }
                ],
            },
        )

    async def mock_openrouter(
        safe_message, aqi_snapshot, profile, rec_package, top_recs, history
    ):
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as hc:
            return await GeminiService._call_openrouter(
                custom_app.state.gemini_service,
                safe_message,
                aqi_snapshot,
                profile,
                rec_package,
                top_recs,
                history,
                client=hc,
            )

    custom_app.state.aqi_service.get_current_aqi = mock_aqi
    custom_app.state.gemini_service._call_openrouter = mock_openrouter

    client = TestClient(custom_app)
    res = client.post("/api/chat", json={"message": "Is it safe to jog?", "city": "Delhi"})

    assert res.status_code == 200
    data = res.json()
    assert captured_models == ["openrouter/free"]
    assert data["ai_provider"] == "openrouter (google/gemma-4-26b-a4b-it:free)"
    assert "215" in data["reply"]


def test_openrouter_null_content_falls_back_to_next_free_model():
    or_settings = Settings(
        openrouter_api_key="sk-or-test-key",
        openrouter_model="openrouter/free",
        gemini_api_key="",
        app_env="test",
    )
    custom_app = create_app(settings=or_settings)

    async def mock_aqi(city: str):
        return make_snapshot(city=city, aqi=180)

    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        req_model = json.loads(request.content.decode("utf-8"))["model"]
        if attempts["count"] == 1:
            return httpx.Response(200, json={"choices": [{"message": {"content": None}}]})
        return httpx.Response(
            200,
            json={
                "model": req_model,
                "choices": [{"message": {"content": "Use HEPA filtration at AQI 180."}}],
            },
        )

    async def mock_openrouter(
        safe_message, aqi_snapshot, profile, rec_package, top_recs, history
    ):
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as hc:
            return await GeminiService._call_openrouter(
                custom_app.state.gemini_service,
                safe_message,
                aqi_snapshot,
                profile,
                rec_package,
                top_recs,
                history,
                client=hc,
            )

    custom_app.state.aqi_service.get_current_aqi = mock_aqi
    custom_app.state.gemini_service._call_openrouter = mock_openrouter

    client = TestClient(custom_app)
    res = client.post("/api/chat", json={"message": "Ventilation advice?", "city": "Delhi"})

    assert res.status_code == 200
    assert attempts["count"] == 2
    assert "HEPA filtration" in res.json()["reply"]
