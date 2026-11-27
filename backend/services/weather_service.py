"""Weather retrieval service with OpenWeatherMap, keyless Open-Meteo, and offline fallback."""

import logging

import httpx

from config import Settings, get_settings
from models.schemas import WeatherData
from services.cache_service import TTLCache
from utils.constants import CITY_FALLBACK_PROFILES

logger = logging.getLogger(__name__)

_WEATHER_CODE_LABELS: dict[int, str] = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog / Smog Haze",
    48: "Dense Freezing Fog",
    51: "Light Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    71: "Light Snow",
    80: "Rain Showers",
}


def compute_smog_dispersion(
    temp_c: float | None,
    humidity_pct: float | None,
    wind_speed_kmh: float | None,
) -> tuple[str, str]:
    """Assess winter smog trapping / thermal inversion risk from meteorology."""
    wind = wind_speed_kmh if wind_speed_kmh is not None else 10.0
    temp = temp_c if temp_c is not None else 18.0
    humidity = humidity_pct if humidity_pct is not None else 60.0

    if wind < 7.0 and (temp < 18.0 or humidity >= 70.0):
        return (
            "high",
            "Stagnant winds (<7 km/h) with cool/humid air trap pollutants near ground level.",
        )
    if wind < 13.0:
        return (
            "moderate",
            "Light winds allow slow dispersion; avoid peak morning/evening smog buildup.",
        )
    return (
        "low",
        "Breezy conditions help disperse surface particulates faster than calm days.",
    )


class WeatherService:
    """Fetches current weather and smog dispersion insights for a location."""

    def __init__(self, settings: Settings | None = None, cache: TTLCache | None = None) -> None:
        self._settings = settings or get_settings()
        self._cache = cache or TTLCache(
            ttl_seconds=self._settings.cache_ttl_seconds,
            max_entries=self._settings.cache_max_entries,
        )

    async def get_weather(
        self,
        city: str,
        latitude: float | None = None,
        longitude: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> WeatherData:
        """Fetch weather via OpenWeatherMap (if configured) or keyless Open-Meteo."""
        cache_key = f"weather:{city.lower()}:{latitude}:{longitude}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        close_client = client is None
        http_client = client or httpx.AsyncClient(timeout=self._settings.request_timeout_seconds)
        try:
            data: WeatherData | None = None
            if self._settings.has_openweather:
                data = await self._fetch_openweather(city, http_client)

            if data is None and latitude is not None and longitude is not None:
                data = await self._fetch_open_meteo(latitude, longitude, http_client)

            if data is None:
                data = self._fallback_weather(city)

            self._cache.set(cache_key, data)
            return data
        finally:
            if close_client:
                await http_client.aclose()

    async def _fetch_openweather(
        self, city: str, client: httpx.AsyncClient
    ) -> WeatherData | None:
        """Fetch current weather from OpenWeatherMap API."""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self._settings.openweather_api_key,
            "units": "metric",
        }
        try:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return None
            payload = resp.json()
            main = payload.get("main", {})
            wind_ms = payload.get("wind", {}).get("speed")
            wind_kmh = round(float(wind_ms) * 3.6, 1) if wind_ms is not None else None
            temp_c = main.get("temp")
            humidity = main.get("humidity")
            weather_list = payload.get("weather") or [{}]
            condition = weather_list[0].get("description", "Clear").title()
            risk, note = compute_smog_dispersion(temp_c, humidity, wind_kmh)
            return WeatherData(
                temperature_c=round(float(temp_c), 1) if temp_c is not None else None,
                humidity_pct=float(humidity) if humidity is not None else None,
                wind_speed_kmh=wind_kmh,
                condition=condition,
                smog_trapping_risk=risk,  # type: ignore[arg-type]
                dispersion_note=note,
                data_source="openweathermap",
            )
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            logger.warning("OpenWeatherMap request failed for %s: %s", city, exc)
            return None

    async def _fetch_open_meteo(
        self, latitude: float, longitude: float, client: httpx.AsyncClient
    ) -> WeatherData | None:
        """Fetch current weather from keyless Open-Meteo Forecast API."""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "wind_speed_unit": "kmh",
        }
        try:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return None
            current = resp.json().get("current", {})
            temp_c = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind_kmh = current.get("wind_speed_10m")
            wmo_code = int(current.get("weather_code", 0))
            condition = _WEATHER_CODE_LABELS.get(wmo_code, "Urban Haze")
            risk, note = compute_smog_dispersion(temp_c, humidity, wind_kmh)
            return WeatherData(
                temperature_c=round(float(temp_c), 1) if temp_c is not None else None,
                humidity_pct=float(humidity) if humidity is not None else None,
                wind_speed_kmh=round(float(wind_kmh), 1) if wind_kmh is not None else None,
                condition=condition,
                smog_trapping_risk=risk,  # type: ignore[arg-type]
                dispersion_note=note,
                data_source="open-meteo",
            )
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            logger.warning("Open-Meteo weather request failed: %s", exc)
            return None

    def _fallback_weather(self, city: str) -> WeatherData:
        """Return baseline weather metrics when external weather APIs are unavailable."""
        profile = CITY_FALLBACK_PROFILES.get(city.lower().strip())
        if profile:
            risk, note = compute_smog_dispersion(
                profile["temp_c"], profile["humidity"], profile["wind_kmh"]
            )
            return WeatherData(
                temperature_c=profile["temp_c"],
                humidity_pct=profile["humidity"],
                wind_speed_kmh=profile["wind_kmh"],
                condition=profile["condition"],
                smog_trapping_risk=risk,  # type: ignore[arg-type]
                dispersion_note=note,
                data_source="fallback",
            )
        risk, note = compute_smog_dispersion(16.0, 65.0, 7.5)
        return WeatherData(
            temperature_c=16.0,
            humidity_pct=65.0,
            wind_speed_kmh=7.5,
            condition="Haze",
            smog_trapping_risk=risk,  # type: ignore[arg-type]
            dispersion_note=note,
            data_source="fallback",
        )
