"""Air Quality Index orchestrator with WAQI, Google AQI, Open-Meteo, caching & fallback."""

import logging
from datetime import datetime, timezone

import httpx

from config import Settings, get_settings
from models.schemas import AQISnapshot, PollutantDetails
from services.aqi_providers import (
    fetch_google_air_quality,
    fetch_waqi_by_city,
    synthesize_diurnal_trend,
)
from services.cache_service import TTLCache
from services.open_meteo_aqi import fetch_open_meteo_aqi
from services.reverse_geocode import reverse_geocode
from services.weather_service import WeatherService
from utils.aqi_calculator import calculate_overall_aqi, get_aqi_category
from utils.constants import CITY_FALLBACK_PROFILES
from utils.validators import validate_city_name

logger = logging.getLogger(__name__)


class CityNotFoundError(Exception):
    """Raised when a requested city cannot be resolved to an air quality location."""


class ExternalServiceError(Exception):
    """Raised when all upstream AQI services fail and no fallback profile matches."""


class AQIService:
    """Retrieves, normalizes, and caches real-time AQI and pollutant readings."""

    def __init__(
        self,
        settings: Settings | None = None,
        cache: TTLCache | None = None,
        weather_service: WeatherService | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._cache = cache or TTLCache(
            ttl_seconds=self._settings.cache_ttl_seconds,
            max_entries=self._settings.cache_max_entries,
        )
        self._weather_service = weather_service or WeatherService(
            settings=self._settings, cache=self._cache
        )

    async def get_current_aqi(
        self, city: str, client: httpx.AsyncClient | None = None
    ) -> AQISnapshot:
        """Return live (or cached) AQI snapshot for a validated city name."""
        normalized_city = validate_city_name(city)
        cache_key = f"aqi:city:{normalized_city.lower()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached.model_copy(update={"cached": True})

        close_client = client is None
        http_client = client or httpx.AsyncClient(timeout=self._settings.request_timeout_seconds)
        try:
            snapshot: AQISnapshot | None = None
            if self._settings.has_waqi:
                snapshot = await fetch_waqi_by_city(
                    normalized_city, self._settings, self._weather_service, http_client
                )
            if snapshot is None:
                snapshot = await self._fetch_by_geocoded_city(normalized_city, http_client)

            self._cache.set(cache_key, snapshot)
            return snapshot
        except CityNotFoundError:
            raise
        except (httpx.HTTPError, ExternalServiceError) as exc:
            logger.warning("Upstream AQI lookup failed for %s: %s", normalized_city, exc)
            fallback = await self._fallback_snapshot(normalized_city)
            if fallback is not None:
                self._cache.set(cache_key, fallback, ttl_seconds=180)
                return fallback
            raise ExternalServiceError(
                f"Unable to retrieve live air quality data for '{normalized_city}' right now."
            ) from exc
        finally:
            if close_client:
                await http_client.aclose()

    async def get_aqi_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        label: str = "Your Location",
        client: httpx.AsyncClient | None = None,
    ) -> AQISnapshot:
        """Return live AQI snapshot using geographic coordinates from browser geolocation."""
        cache_key = f"aqi:geo:{round(latitude, 2)}:{round(longitude, 2)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached.model_copy(update={"cached": True})

        close_client = client is None
        http_client = client or httpx.AsyncClient(timeout=self._settings.request_timeout_seconds)
        try:
            # Reverse geocode to get a human-readable city name
            resolved_name = await reverse_geocode(latitude, longitude, http_client)
            display_name = resolved_name or label

            snapshot = None
            if self._settings.has_google_aqi:
                snapshot = await fetch_google_air_quality(
                    display_name, display_name, "", latitude, longitude,
                    self._settings, self._weather_service, http_client,
                )
            if snapshot is None:
                snapshot = await fetch_open_meteo_aqi(
                    display_name, display_name, "", latitude, longitude,
                    self._weather_service, http_client,
                )
            if snapshot is None:
                raise ExternalServiceError(
                    "Unable to retrieve air quality data for coordinates "
                    f"({latitude}, {longitude})."
                )
            snapshot = snapshot.model_copy(update={"resolved_city": display_name})
            self._cache.set(cache_key, snapshot)
            return snapshot
        finally:
            if close_client:
                await http_client.aclose()

    async def _fetch_by_geocoded_city(
        self, city: str, client: httpx.AsyncClient
    ) -> AQISnapshot:
        """Geocode city with Open-Meteo and query Google AQI or Open-Meteo Air Quality."""
        geo_resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        geo_resp.raise_for_status()
        results = geo_resp.json().get("results") or []
        if not results:
            raise CityNotFoundError(
                f"Could not find air quality monitoring coordinates for '{city}'."
            )

        loc = results[0]
        resolved = str(loc.get("name") or city)
        country = str(loc.get("country") or "")
        lat, lon = float(loc["latitude"]), float(loc["longitude"])

        if self._settings.has_google_aqi:
            google_snap = await fetch_google_air_quality(
                city, resolved, country, lat, lon,
                self._settings, self._weather_service, client,
            )
            if google_snap is not None:
                return google_snap

        return await fetch_open_meteo_aqi(
            city, resolved, country, lat, lon, self._weather_service, client
        )

    async def _fallback_snapshot(self, city: str) -> AQISnapshot | None:
        """Build an offline baseline snapshot for known smog-affected cities."""
        profile = CITY_FALLBACK_PROFILES.get(city.lower().strip())
        if not profile:
            return None

        pollutants = PollutantDetails(
            pm25=profile["pm25"], pm10=profile["pm10"], o3=profile["o3"],
            no2=profile["no2"], so2=profile["so2"], co=profile["co"],
        )
        aqi_val, dominant = calculate_overall_aqi(pollutants)
        category, label, color, text_color, advisory = get_aqi_category(aqi_val)
        weather = await self._weather_service.get_weather(profile["resolved_city"])
        return AQISnapshot(
            city=city,
            resolved_city=profile["resolved_city"],
            country=profile["country"],
            latitude=profile["latitude"],
            longitude=profile["longitude"],
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
            data_source="fallback",
            cached=False,
        )
