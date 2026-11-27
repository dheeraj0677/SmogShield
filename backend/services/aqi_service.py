"""Air Quality Index retrieval service with WAQI, Open-Meteo, caching, and offline resilience."""

import logging
from datetime import datetime, timezone

import httpx

from config import Settings, get_settings
from models.schemas import AQISnapshot, HourlyTrendPoint, PollutantDetails
from services.cache_service import TTLCache
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
                snapshot = await self._fetch_waqi_by_city(normalized_city, http_client)

            if snapshot is None:
                snapshot = await self._fetch_open_meteo_by_city(normalized_city, http_client)

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
            snapshot = await self._fetch_open_meteo_aqi(
                city_query=label,
                resolved_city=label,
                country="",
                latitude=latitude,
                longitude=longitude,
                client=http_client,
            )
            self._cache.set(cache_key, snapshot)
            return snapshot
        finally:
            if close_client:
                await http_client.aclose()

    async def _fetch_waqi_by_city(
        self, city: str, client: httpx.AsyncClient
    ) -> AQISnapshot | None:
        """Query World Air Quality Index (WAQI) API for a city feed."""
        url = f"https://api.waqi.info/feed/{city}/"
        try:
            resp = await client.get(url, params={"token": self._settings.waqi_api_token})
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
                pm25=self._extract_iaqi(iaqi, "pm25"),
                pm10=self._extract_iaqi(iaqi, "pm10"),
                o3=self._extract_iaqi(iaqi, "o3"),
                no2=self._extract_iaqi(iaqi, "no2"),
                so2=self._extract_iaqi(iaqi, "so2"),
                co=self._extract_iaqi(iaqi, "co"),
            )
            city_meta = data.get("city", {})
            geo = city_meta.get("geo") or []
            lat = float(geo[0]) if len(geo) >= 2 else None
            lon = float(geo[1]) if len(geo) >= 2 else None
            resolved = str(city_meta.get("name") or city).split(",")[0].strip()

            aqi_val = max(0, min(500, int(round(raw_aqi))))
            category, label, color, text_color, advisory = get_aqi_category(aqi_val)
            dominant = str(data.get("dominentpol") or "pm25").lower()
            weather = await self._weather_service.get_weather(resolved, lat, lon, client=client)

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
                dominant_pollutant=dominant,
                pollutants=pollutants,
                weather=weather,
                hourly_trend=self._synthesize_diurnal_trend(aqi_val, pollutants.pm25 or 40.0),
                timestamp=datetime.now(timezone.utc).isoformat(),
                data_source="waqi",
                cached=False,
            )
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            logger.warning("WAQI lookup failed for %s: %s", city, exc)
            return None

    async def _fetch_open_meteo_by_city(
        self, city: str, client: httpx.AsyncClient
    ) -> AQISnapshot:
        """Geocode city with Open-Meteo and query its Air Quality API."""
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = await client.get(
            geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"}
        )
        geo_resp.raise_for_status()
        results = geo_resp.json().get("results") or []
        if not results:
            raise CityNotFoundError(
                f"Could not find air quality monitoring coordinates for '{city}'."
            )

        loc = results[0]
        return await self._fetch_open_meteo_aqi(
            city_query=city,
            resolved_city=str(loc.get("name") or city),
            country=str(loc.get("country") or ""),
            latitude=float(loc["latitude"]),
            longitude=float(loc["longitude"]),
            client=client,
        )

    async def _fetch_open_meteo_aqi(
        self,
        city_query: str,
        resolved_city: str,
        country: str,
        latitude: float,
        longitude: float,
        client: httpx.AsyncClient,
    ) -> AQISnapshot:
        """Fetch live pollutant concentrations from Open-Meteo Air Quality API."""
        aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "us_aqi,pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
            ),
            "hourly": "pm2_5,us_aqi",
            "forecast_days": 1,
        }
        resp = await client.get(aqi_url, params=params)
        resp.raise_for_status()
        payload = resp.json()
        current = payload.get("current", {})

        # Open-Meteo reports CO in µg/m³; convert to mg/m³ for US EPA scale
        raw_co = current.get("carbon_monoxide")
        co_mg = round(float(raw_co) / 1000.0, 2) if raw_co is not None else None

        pollutants = PollutantDetails(
            pm25=self._round_opt(current.get("pm2_5")),
            pm10=self._round_opt(current.get("pm10")),
            o3=self._round_opt(current.get("ozone")),
            no2=self._round_opt(current.get("nitrogen_dioxide")),
            so2=self._round_opt(current.get("sulphur_dioxide")),
            co=co_mg,
        )

        computed_aqi, dominant = calculate_overall_aqi(pollutants)
        api_us_aqi = current.get("us_aqi")
        # Prefer EPA computed sub-index from fresh pollutants when available, else api_us_aqi
        aqi_val = (
            computed_aqi
            if pollutants.pm25 is not None or pollutants.pm10 is not None
            else int(round(float(api_us_aqi)))
            if api_us_aqi is not None
            else computed_aqi
        )
        aqi_val = max(0, min(500, aqi_val))

        category, label, color, text_color, advisory = get_aqi_category(aqi_val)
        weather = await self._weather_service.get_weather(
            resolved_city, latitude, longitude, client=client
        )
        hourly_trend = self._extract_hourly_trend(payload.get("hourly", {}))
        if not hourly_trend:
            hourly_trend = self._synthesize_diurnal_trend(aqi_val, pollutants.pm25 or 35.0)

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

    async def _fallback_snapshot(self, city: str) -> AQISnapshot | None:
        """Build an offline baseline snapshot for known smog-affected cities."""
        profile = CITY_FALLBACK_PROFILES.get(city.lower().strip())
        if not profile:
            return None

        pollutants = PollutantDetails(
            pm25=profile["pm25"],
            pm10=profile["pm10"],
            o3=profile["o3"],
            no2=profile["no2"],
            so2=profile["so2"],
            co=profile["co"],
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
            hourly_trend=self._synthesize_diurnal_trend(aqi_val, pollutants.pm25 or 35.0),
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_source="fallback",
            cached=False,
        )

    @staticmethod
    def _extract_hourly_trend(hourly: dict) -> list[HourlyTrendPoint]:
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
            hour_str = str(raw_time)[-5:]
            pm_float = max(0.0, round(float(pm_raw or 0.0), 1))
            aqi_int = max(0, min(500, int(round(float(aqi_raw or 0)))))
            trend.append(HourlyTrendPoint(hour=hour_str, aqi=aqi_int, pm25=pm_float))
        return trend

    @staticmethod
    def _synthesize_diurnal_trend(
        base_aqi: int, base_pm25: float
    ) -> list[HourlyTrendPoint]:
        """Build a realistic winter-inversion diurnal profile when hourly series is absent."""
        # Morning & late-evening inversion peaks; midday mixing trough
        factors = [1.14, 1.10, 1.06, 1.04, 1.12, 1.22, 1.25, 1.18, 1.02, 0.88, 0.78, 0.72]
        hours = [
            "00:00", "02:00", "04:00", "06:00", "08:00", "10:00",
            "12:00", "14:00", "16:00", "18:00", "20:00", "22:00",
        ]
        # Shift trough to midday and spike to evening
        curve = [1.08, 1.04, 1.02, 1.12, 1.22, 1.15, 0.90, 0.74, 0.78, 0.98, 1.18, 1.20]
        del factors
        return [
            HourlyTrendPoint(
                hour=h,
                aqi=max(5, min(500, int(round(base_aqi * f)))),
                pm25=max(1.0, round(base_pm25 * f, 1)),
            )
            for h, f in zip(hours, curve, strict=True)
        ]

    @staticmethod
    def _extract_iaqi(iaqi: dict, key: str) -> float | None:
        val = iaqi.get(key, {}).get("v")
        return round(float(val), 1) if isinstance(val, (int, float)) else None

    @staticmethod
    def _round_opt(val: float | int | None) -> float | None:
        return round(float(val), 1) if isinstance(val, (int, float)) else None
