"""Open-Meteo keyless Air Quality API adapter."""

from datetime import datetime, timezone

import httpx

from models.schemas import AQISnapshot, PollutantDetails
from services.aqi_providers import (
    extract_hourly_trend,
    round_opt,
    synthesize_diurnal_trend,
)
from services.weather_service import WeatherService
from utils.aqi_calculator import calculate_overall_aqi, get_aqi_category


async def fetch_open_meteo_aqi(
    city_query: str,
    resolved_city: str,
    country: str,
    latitude: float,
    longitude: float,
    weather_service: WeatherService,
    client: httpx.AsyncClient,
) -> AQISnapshot:
    """Fetch live pollutant concentrations and 24h trend from Open-Meteo."""
    resp = await client.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "us_aqi,pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
            ),
            "hourly": "pm2_5,us_aqi",
            "forecast_days": 1,
        },
    )
    resp.raise_for_status()
    payload = resp.json()
    current = payload.get("current", {})

    raw_co = current.get("carbon_monoxide")
    co_mg = round(float(raw_co) / 1000.0, 2) if raw_co is not None else None
    pollutants = PollutantDetails(
        pm25=round_opt(current.get("pm2_5")),
        pm10=round_opt(current.get("pm10")),
        o3=round_opt(current.get("ozone")),
        no2=round_opt(current.get("nitrogen_dioxide")),
        so2=round_opt(current.get("sulphur_dioxide")),
        co=co_mg,
    )

    computed_aqi, dominant = calculate_overall_aqi(pollutants)
    api_us_aqi = current.get("us_aqi")
    aqi_val = (
        computed_aqi
        if pollutants.pm25 is not None or pollutants.pm10 is not None
        else int(round(float(api_us_aqi)))
        if api_us_aqi is not None
        else computed_aqi
    )
    aqi_val = max(0, min(500, aqi_val))
    category, label, color, text_color, advisory = get_aqi_category(aqi_val)
    weather = await weather_service.get_weather(
        resolved_city, latitude, longitude, client=client
    )
    hourly_trend = extract_hourly_trend(payload.get("hourly", {}))
    if not hourly_trend:
        hourly_trend = synthesize_diurnal_trend(aqi_val, pollutants.pm25 or 35.0)

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
        hourly_trend=hourly_trend,
        timestamp=datetime.now(timezone.utc).isoformat(),
        data_source="open-meteo",
        cached=False,
    )
