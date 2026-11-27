"""Upstream AQI provider adapters: WAQI, Google Air Quality API v1, and Open-Meteo."""

import logging
from datetime import datetime, timezone

import httpx

from config import Settings
from models.schemas import AQISnapshot, HourlyTrendPoint, PollutantDetails
from services.weather_service import WeatherService
from utils.aqi_calculator import calculate_overall_aqi, get_aqi_category

logger = logging.getLogger(__name__)


def round_opt(val: float | int | None) -> float | None:
    """Round optional numeric pollutant measurements cleanly."""
    return round(float(val), 1) if isinstance(val, (int, float)) else None


def extract_hourly_trend(hourly: dict) -> list[HourlyTrendPoint]:
    """Parse up to 24 hourly trend points from Open-Meteo hourly arrays."""
    times = hourly.get("time") or []
    pm_vals = hourly.get("pm2_5") or []
    aqi_vals = hourly.get("us_aqi") or []
    trend: list[HourlyTrendPoint] = []
    for idx, raw_time in enumerate(times[:24]):
        pm_raw = pm_vals[idx] if idx < len(pm_vals) else None
        aqi_raw = aqi_vals[idx] if idx < len(aqi_vals) else None
        if pm_raw is None and aqi_raw is None:
            continue
        trend.append(
            HourlyTrendPoint(
                hour=str(raw_time)[-5:],
                aqi=max(0, min(500, int(round(float(aqi_raw or 0))))),
                pm25=max(0.0, round(float(pm_raw or 0.0), 1)),
            )
        )
    return trend


def synthesize_diurnal_trend(base_aqi: int, base_pm25: float) -> list[HourlyTrendPoint]:
    """Build a realistic winter-inversion diurnal profile when hourly series is absent."""
    hours = [
        "00:00", "02:00", "04:00", "06:00", "08:00", "10:00",
        "12:00", "14:00", "16:00", "18:00", "20:00", "22:00",
    ]
    curve = [1.08, 1.04, 1.02, 1.12, 1.22, 1.15, 0.90, 0.74, 0.78, 0.98, 1.18, 1.20]
    return [
        HourlyTrendPoint(
            hour=h,
            aqi=max(5, min(500, int(round(base_aqi * f)))),
            pm25=max(1.0, round(base_pm25 * f, 1)),
        )
        for h, f in zip(hours, curve, strict=True)
    ]


async def fetch_waqi_by_city(
    city: str,
    settings: Settings,
    weather_service: WeatherService,
    client: httpx.AsyncClient,
) -> AQISnapshot | None:
    """Query World Air Quality Index (WAQI) API for a city feed."""
    url = f"https://api.waqi.info/feed/{city}/"
    try:
        resp = await client.get(url, params={"token": settings.waqi_api_token})
        if resp.status_code != 200:
            return None
        payload = resp.json()
        if payload.get("status") != "ok":
            return None

        data = payload.get("data", {})
        raw_aqi = data.get("aqi")
        if not isinstance(raw_aqi, (int, float)):
            return None

        iaqi = data.get("iaqi", {})
        pollutants = PollutantDetails(
            pm25=round_opt(iaqi.get("pm25", {}).get("v")),
            pm10=round_opt(iaqi.get("pm10", {}).get("v")),
            o3=round_opt(iaqi.get("o3", {}).get("v")),
            no2=round_opt(iaqi.get("no2", {}).get("v")),
            so2=round_opt(iaqi.get("so2", {}).get("v")),
            co=round_opt(iaqi.get("co", {}).get("v")),
        )
        city_meta = data.get("city", {})
        geo = city_meta.get("geo") or []
        lat = float(geo[0]) if len(geo) >= 2 else None
        lon = float(geo[1]) if len(geo) >= 2 else None
        resolved = str(city_meta.get("name") or city).split(",")[0].strip()

        aqi_val = max(0, min(500, int(round(raw_aqi))))
        category, label, color, text_color, advisory = get_aqi_category(aqi_val)
        weather = await weather_service.get_weather(resolved, lat, lon, client=client)

        return AQISnapshot(
            city=city,
            resolved_city=resolved,
            country="",
            latitude=lat,
            longitude=lon,
            aqi=aqi_val,
            category=category,
            category_label=label,
            color=color,
            text_color=text_color,
            health_advisory=advisory,
            dominant_pollutant=str(data.get("dominentpol") or "pm25").lower(),
            pollutants=pollutants,
            weather=weather,
            hourly_trend=synthesize_diurnal_trend(aqi_val, pollutants.pm25 or 40.0),
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="waqi",
            cached=False,
        )
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("WAQI lookup failed for %s: %s", city, exc)
        return None


async def fetch_google_air_quality(
    city_query: str,
    resolved_city: str,
    country: str,
    latitude: float,
    longitude: float,
    settings: Settings,
    weather_service: WeatherService,
    client: httpx.AsyncClient,
) -> AQISnapshot | None:
    """Query Google Air Quality API v1 currentConditions:lookup when configured."""
    url = "https://airquality.googleapis.com/v1/currentConditions:lookup"
    body = {
        "location": {"latitude": latitude, "longitude": longitude},
        "extraComputations": ["POLLUTANT_CONCENTRATION", "DOMINANT_POLLUTANT_CONCENTRATION"],
    }
    try:
        resp = await client.post(
            url, params={"key": settings.google_air_quality_api_key}, json=body
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        pollutant_map: dict[str, float | None] = {}
        for item in data.get("pollutants", []):
            code = str(item.get("code", "")).lower()
            val = item.get("concentration", {}).get("value")
            if isinstance(val, (int, float)):
                pollutant_map[code] = round(float(val), 1)

        pollutants = PollutantDetails(
            pm25=pollutant_map.get("pm25"),
            pm10=pollutant_map.get("pm10"),
            o3=pollutant_map.get("o3"),
            no2=pollutant_map.get("no2"),
            so2=pollutant_map.get("so2"),
            co=pollutant_map.get("co"),
        )
        aqi_val, dominant = calculate_overall_aqi(pollutants)
        category, label, color, text_color, advisory = get_aqi_category(aqi_val)
        weather = await weather_service.get_weather(
            resolved_city, latitude, longitude, client=client
        )
        return AQISnapshot(
            city=city_query,
            resolved_city=resolved_city,
            country=country,
            latitude=latitude,
            longitude=longitude,
            aqi=aqi_val,
            category=category,
            category_label=label,
            color=color,
            text_color=text_color,
            health_advisory=advisory,
            dominant_pollutant=dominant,
            pollutants=pollutants,
            weather=weather,
            hourly_trend=synthesize_diurnal_trend(aqi_val, pollutants.pm25 or 35.0),
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="google-air-quality",
            cached=False,
        )
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("Google Air Quality API failed for %s: %s", resolved_city, exc)
        return None
