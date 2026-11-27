"""Tests for Google Air Quality API and OpenWeatherMap dispersion integration."""

import httpx
import pytest

from config import Settings
from services.aqi_service import AQIService
from services.weather_service import WeatherService


@pytest.mark.asyncio
async def test_weather_service_openweathermap_and_dispersion_levels():
    owm_settings = Settings(openweather_api_key="test-key", app_env="test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "main": {"temp": 22.0, "humidity": 50},
                "wind": {"speed": 4.5},
                "weather": [{"description": "clear sky"}],
            },
        )

    transport = httpx.MockTransport(handler)
    service = WeatherService(settings=owm_settings)
    async with httpx.AsyncClient(transport=transport) as http_client:
        weather = await service.get_weather("London", client=http_client)

    assert weather.data_source == "openweathermap"
    assert weather.wind_speed_kmh == 16.2
    assert weather.smog_trapping_risk == "low"


@pytest.mark.asyncio
async def test_aqi_service_uses_google_air_quality_when_configured():
    google_settings = Settings(google_air_quality_api_key="test-google-key", app_env="test")

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "geocoding-api.open-meteo.com" in url:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "Delhi",
                            "country": "India",
                            "latitude": 28.6139,
                            "longitude": 77.2090,
                        }
                    ]
                },
            )
        if "airquality.googleapis.com" in url:
            return httpx.Response(
                200,
                json={
                    "pollutants": [
                        {"code": "pm25", "concentration": {"value": 140.0}},
                        {"code": "pm10", "concentration": {"value": 210.0}},
                        {"code": "no2", "concentration": {"value": 55.0}},
                    ]
                },
            )
        if "api.open-meteo.com/v1/forecast" in url:
            return httpx.Response(
                200,
                json={
                    "current": {
                        "temperature_2m": 14.0,
                        "relative_humidity_2m": 72.0,
                        "wind_speed_10m": 5.0,
                        "weather_code": 45,
                    }
                },
            )
        return httpx.Response(404)

    service = AQIService(settings=google_settings)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as hc:
        snapshot = await service.get_current_aqi("Delhi", client=hc)

    assert snapshot.data_source == "google-air-quality"
    assert snapshot.pollutants.pm25 == 140.0
    assert snapshot.aqi > 200
