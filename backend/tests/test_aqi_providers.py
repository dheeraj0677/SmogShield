"""Tests for WAQI, Google Air Quality, reverse geocoding, and IP location providers."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from config import Settings
from services.aqi_providers import (
    fetch_google_air_quality,
    fetch_waqi_by_city,
    round_opt,
)
from services.reverse_geocode import lookup_ip_location, reverse_geocode
from services.weather_service import WeatherService


def _mock_response(status_code: int, payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    return resp


def test_round_opt_handles_none_and_numeric():
    assert round_opt(None) is None
    assert round_opt(12.345) == 12.3


@pytest.mark.asyncio
async def test_fetch_waqi_by_city_success_and_failures():
    settings = Settings(waqi_api_token="demo-token")
    weather = WeatherService(settings=settings)
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.return_value = _mock_response(
        200,
        {
            "status": "ok",
            "data": {
                "aqi": 142,
                "dominentpol": "pm25",
                "iaqi": {"pm25": {"v": 55.4}, "pm10": {"v": 90.0}},
                "city": {"name": "Delhi, India", "geo": [28.61, 77.2]},
            },
        },
    )
    snap = await fetch_waqi_by_city("Delhi", settings, weather, client)
    assert snap is not None
    assert snap.aqi == 142
    assert snap.data_source == "waqi"
    assert snap.resolved_city == "Delhi"

    client.get.return_value = _mock_response(500, {})
    assert await fetch_waqi_by_city("Delhi", settings, weather, client) is None

    client.get.return_value = _mock_response(200, {"status": "error"})
    assert await fetch_waqi_by_city("Delhi", settings, weather, client) is None

    client.get.side_effect = httpx.ConnectError("down")
    assert await fetch_waqi_by_city("Delhi", settings, weather, client) is None


@pytest.mark.asyncio
async def test_fetch_google_air_quality_success_and_fallback():
    settings = Settings(google_air_quality_api_key="demo-google-key")
    weather = WeatherService(settings=settings)
    client = AsyncMock(spec=httpx.AsyncClient)
    client.post.return_value = _mock_response(
        200,
        {
            "pollutants": [
                {"code": "pm25", "concentration": {"value": 45.6}},
                {"code": "pm10", "concentration": {"value": 80.2}},
            ]
        },
    )
    snap = await fetch_google_air_quality(
        "Delhi", "Delhi", "India", 28.61, 77.2, settings, weather, client
    )
    assert snap is not None
    assert snap.data_source == "google-air-quality"
    assert snap.pollutants.pm25 == 45.6

    client.post.return_value = _mock_response(403, {})
    assert (
        await fetch_google_air_quality(
            "Delhi", "Delhi", "India", 28.61, 77.2, settings, weather, client
        )
        is None
    )

    client.post.side_effect = httpx.ReadTimeout("timeout")
    assert (
        await fetch_google_air_quality(
            "Delhi", "Delhi", "India", 28.61, 77.2, settings, weather, client
        )
        is None
    )


@pytest.mark.asyncio
async def test_reverse_geocode_and_ip_lookup():
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.return_value = _mock_response(200, {"results": [{"name": "Hyderabad"}]})
    assert await reverse_geocode(17.38, 78.48, client) == "Hyderabad"

    client.get.side_effect = [
        _mock_response(500, {}),
        _mock_response(200, {"address": {"city": "Pune"}}),
    ]
    assert await reverse_geocode(18.52, 73.85, client) == "Pune"

    client.get.side_effect = None
    client.get.return_value = _mock_response(
        200, {"success": True, "latitude": 17.38, "longitude": 78.48, "city": "Hyderabad"}
    )
    loc = await lookup_ip_location("8.8.8.8", client)
    assert loc == (17.38, 78.48, "Hyderabad")

    client.get.return_value = _mock_response(500, {})
    assert await lookup_ip_location("127.0.0.1", client) is None
