"""Integration tests for API route error paths, IP geolocation, and health flags."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from main import create_app
from services.aqi_service import CityNotFoundError, ExternalServiceError


def test_aqi_route_error_paths(client):
    app = client.app
    original = app.state.aqi_service.get_current_aqi

    app.state.aqi_service.get_current_aqi = AsyncMock(side_effect=ValueError("bad city"))
    assert client.get("/api/aqi/TestCity").status_code == 400

    app.state.aqi_service.get_current_aqi = AsyncMock(side_effect=CityNotFoundError("unknown"))
    assert client.get("/api/aqi/Atlantis").status_code == 404
    assert client.post(
        "/api/recommendations", json={"city": "Atlantis"}
    ).status_code == 404
    assert client.post(
        "/api/chat", json={"message": "hello", "city": "Atlantis"}
    ).status_code == 404

    app.state.aqi_service.get_current_aqi = AsyncMock(side_effect=ExternalServiceError("down"))
    assert client.get("/api/aqi/Delhi").status_code == 503
    assert client.post(
        "/api/recommendations", json={"city": "Delhi"}
    ).status_code == 503
    assert client.post(
        "/api/chat", json={"message": "hello", "city": "Delhi"}
    ).status_code == 503

    app.state.aqi_service.get_current_aqi = original


def test_ip_location_and_coordinates_routes(client, monkeypatch):
    monkeypatch.setattr(
        "api.routes.aqi.lookup_ip_location",
        AsyncMock(return_value=(17.38, 78.48, "Hyderabad")),
    )
    resp = client.get("/api/aqi/ip-location")
    assert resp.status_code == 200
    assert resp.json()["aqi"] >= 0

    monkeypatch.setattr("api.routes.aqi.lookup_ip_location", AsyncMock(return_value=None))
    assert client.get("/api/aqi/ip-location").status_code == 503

    original_coords = client.app.state.aqi_service.get_aqi_by_coordinates
    client.app.state.aqi_service.get_aqi_by_coordinates = AsyncMock(
        side_effect=ExternalServiceError("coord fail")
    )
    assert client.get("/api/aqi/coordinates?lat=28.6&lon=77.2").status_code == 503
    client.app.state.aqi_service.get_aqi_by_coordinates = original_coords


def test_health_reports_configured_services():
    from config import Settings

    app = create_app(
        settings=Settings(
            gemini_api_key="fake-gem",
            google_air_quality_api_key="fake-gaq",
            openweather_api_key="fake-owm",
            waqi_api_token="fake-waqi",
        )
    )
    resp = TestClient(app).get("/api/health")
    assert resp.status_code == 200
    services = resp.json()["services"]
    assert services["google_air_quality"] == "configured"
    assert "openweathermap" in services["weather"]
    assert "waqi" in services["aqi"]
