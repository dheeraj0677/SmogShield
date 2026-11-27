"""Shared pytest fixtures for SmogShield backend tests."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from config import Settings
from main import create_app
from models.enums import AQICategory
from models.schemas import AQISnapshot, PollutantDetails, WeatherData


def make_snapshot(
    city: str = "Delhi",
    aqi: int = 285,
    pm25: float = 178.0,
    category: AQICategory = AQICategory.VERY_UNHEALTHY,
    label: str = "Very Unhealthy",
) -> AQISnapshot:
    """Create a deterministic AQISnapshot for isolated unit and API tests."""
    return AQISnapshot(
        city=city,
        resolved_city=city,
        country="India",
        latitude=28.6139,
        longitude=77.2090,
        aqi=aqi,
        category=category,
        category_label=label,
        color="#7e22ce",
        text_color="#ffffff",
        health_advisory="Stay indoors with filtered air.",
        dominant_pollutant="pm25",
        pollutants=PollutantDetails(
            pm25=pm25, pm10=260.0, o3=42.0, no2=65.0, so2=18.0, co=2.1
        ),
        weather=WeatherData(
            temperature_c=14.0,
            humidity_pct=75.0,
            wind_speed_kmh=5.0,
            condition="Dense Haze",
            smog_trapping_risk="high",
            dispersion_note="Stagnant winds trap pollutants near ground level.",
            data_source="test",
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
        data_source="test",
        cached=False,
    )


@pytest.fixture(autouse=True)
def _isolate_env_keys(monkeypatch: pytest.MonkeyPatch):
    """Prevent local .env API keys from causing live external API calls in tests."""
    for var in (
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_AIR_QUALITY_API_KEY",
        "WAQI_API_TOKEN",
        "OPENWEATHER_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def test_settings() -> Settings:
    """Return isolated settings without external API keys."""
    return Settings(
        gemini_api_key="",
        openrouter_api_key="",
        google_air_quality_api_key="",
        waqi_api_token="",
        openweather_api_key="",
        app_env="test",
        rate_limit_chat_per_min=30,
        rate_limit_aqi_per_min=60,
    )


@pytest.fixture
def app(test_settings: Settings):
    """Return a fresh FastAPI test app instance."""
    return create_app(settings=test_settings)


@pytest.fixture
def client(app) -> TestClient:
    """Return a TestClient bound to the fresh FastAPI app."""
    return TestClient(app)
