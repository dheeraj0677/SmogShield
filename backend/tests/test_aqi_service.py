"""Tests for AQIService caching, Open-Meteo parsing, fallback resilience, and errors."""

import httpx
import pytest

from config import Settings
from services.aqi_service import AQIService, CityNotFoundError
from services.cache_service import TTLCache
from services.weather_service import WeatherService


@pytest.mark.asyncio
async def test_aqi_service_fetches_and_caches_open_meteo(test_settings: Settings):
    call_count = {"geo": 0, "aqi": 0, "weather": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "geocoding-api.open-meteo.com" in url:
            call_count["geo"] += 1
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
        if "air-quality-api.open-meteo.com" in url:
            call_count["aqi"] += 1
            return httpx.Response(
                200,
                json={
                    "current": {
                        "us_aqi": 240,
                        "pm2_5": 165.0,
                        "pm10": 230.0,
                        "carbon_monoxide": 1900.0,
                        "nitrogen_dioxide": 60.0,
                        "sulphur_dioxide": 15.0,
                        "ozone": 45.0,
                    }
                },
            )
        if "api.open-meteo.com/v1/forecast" in url:
            call_count["weather"] += 1
            return httpx.Response(
                200,
                json={
                    "current": {
                        "temperature_2m": 13.2,
                        "relative_humidity_2m": 78.0,
                        "wind_speed_10m": 4.8,
                        "weather_code": 45,
                    }
                },
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    cache = TTLCache(ttl_seconds=600)
    weather_service = WeatherService(settings=test_settings, cache=cache)
    aqi_service = AQIService(
        settings=test_settings, cache=cache, weather_service=weather_service
    )

    async with httpx.AsyncClient(transport=transport) as http_client:
        first = await aqi_service.get_current_aqi("Delhi", client=http_client)
        second = await aqi_service.get_current_aqi("Delhi", client=http_client)

    assert first.resolved_city == "Delhi"
    assert first.cached is False
    assert first.data_source == "open-meteo"
    assert first.aqi > 200
    assert first.weather.smog_trapping_risk == "high"
    assert second.cached is True
    assert call_count == {"geo": 1, "aqi": 1, "weather": 1}


@pytest.mark.asyncio
async def test_aqi_service_raises_not_found_for_unknown_city(test_settings: Settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    transport = httpx.MockTransport(handler)
    service = AQIService(settings=test_settings)
    async with httpx.AsyncClient(transport=transport) as http_client:
        with pytest.raises(CityNotFoundError):
            await service.get_current_aqi("NonexistentCityXYZ", client=http_client)


@pytest.mark.asyncio
async def test_aqi_service_falls_back_on_network_error_for_known_city(
    test_settings: Settings,
):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Network unreachable", request=request)

    transport = httpx.MockTransport(handler)
    service = AQIService(settings=test_settings)
    async with httpx.AsyncClient(transport=transport) as http_client:
        snapshot = await service.get_current_aqi("Lahore", client=http_client)

    assert snapshot.resolved_city == "Lahore"
    assert snapshot.data_source == "fallback"
    assert snapshot.aqi >= 200


def test_aqi_and_recommendations_routes_integration(app, client):
    from tests.conftest import make_snapshot

    async def mock_city(city: str):
        if city.lower() == "unknown":
            raise CityNotFoundError("Unknown city")
        return make_snapshot(city=city, aqi=180)

    async def mock_coords(lat: float, lon: float, label: str = "Your Location"):
        return make_snapshot(city=label, aqi=95)

    app.state.aqi_service.get_current_aqi = mock_city
    app.state.aqi_service.get_aqi_by_coordinates = mock_coords

    res_city = client.get("/api/aqi/Delhi")
    assert res_city.status_code == 200
    assert res_city.json()["aqi"] == 180

    res_404 = client.get("/api/aqi/Unknown")
    assert res_404.status_code == 404

    res_geo = client.get("/api/aqi/coordinates?lat=28.61&lon=77.21")
    assert res_geo.status_code == 200
    assert res_geo.json()["aqi"] == 95

    res_rec = client.get("/api/recommendations/Delhi?has_children=true&health=asthma")
    assert res_rec.status_code == 200
    assert res_rec.json()["effective_aqi"] > 180


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



