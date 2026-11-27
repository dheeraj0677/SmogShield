"""Security tests covering headers, rate limiting, CORS, and error sanitization."""

from fastapi.testclient import TestClient

from config import Settings
from main import create_app
from tests.conftest import make_snapshot


def test_security_headers_are_attached(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in res.headers["Content-Security-Policy"]
    assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_rate_limiter_blocks_excessive_chat_requests():
    settings = Settings(
        rate_limit_chat_per_min=2,
        rate_limit_aqi_per_min=5,
        app_env="test",
    )
    limited_app = create_app(settings=settings)

    async def mock_aqi(city: str):
        return make_snapshot(city=city, aqi=140)

    limited_app.state.aqi_service.get_current_aqi = mock_aqi
    client = TestClient(limited_app)

    r1 = client.post("/api/chat", json={"message": "First", "city": "Delhi"})
    r2 = client.post("/api/chat", json={"message": "Second", "city": "Delhi"})
    r3 = client.post("/api/chat", json={"message": "Third", "city": "Delhi"})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429
    assert "Retry-After" in r3.headers


def test_invalid_city_returns_400_without_stack_trace(client):
    res = client.get("/api/aqi/..%2Fetc%2Fpasswd")
    assert res.status_code in (400, 404)
    assert "Traceback" not in res.text


def test_cors_blocks_unlisted_origin(client):
    res = client.options(
        "/api/health",
        headers={
            "Origin": "https://malicious.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in {k.lower() for k in res.headers}


def test_oversized_body_returns_413_and_wrong_content_type_returns_415(client):
    huge_payload = '{"message": "' + ("a" * 17000) + '", "city": "Delhi"}'
    res_413 = client.post(
        "/api/chat",
        content=huge_payload,
        headers={"Content-Type": "application/json"},
    )
    assert res_413.status_code == 413

    res_415 = client.post(
        "/api/chat",
        content="message=hello",
        headers={"Content-Type": "text/plain"},
    )
    assert res_415.status_code == 415


def test_chat_uses_sha256_cache_on_repeat_query(app, client):
    async def mock_aqi(city: str):
        return make_snapshot(city=city, aqi=210)

    app.state.aqi_service.get_current_aqi = mock_aqi
    payload = {"message": "How to build a DIY filter?", "city": "Delhi"}

    first = client.post("/api/chat", json=payload)
    second = client.post("/api/chat", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert app.state.ai_cache.stats()["hits"] >= 1

