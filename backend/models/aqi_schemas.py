"""AQI, pollutant, weather, and household profile Pydantic schemas."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from models.enums import (
    AQICategory,
    BudgetLevel,
    CommuteType,
    HomeType,
)
from utils.validators import sanitize_text, validate_city_name


class UserProfile(BaseModel):
    """Household context used to personalize routines, hacks, and impact metrics."""

    city: str = Field(default="Delhi", min_length=2, max_length=80)
    family_members: int = Field(default=3, ge=1, le=20)
    has_children: bool = False
    has_elderly: bool = False
    health_conditions: list[str] = Field(default_factory=list, max_length=10)
    commute_type: CommuteType = CommuteType.CAR
    home_type: HomeType = HomeType.APARTMENT
    has_air_purifier: bool = False
    budget: BudgetLevel = BudgetLevel.MEDIUM
    lifestyle_notes: str = Field(default="", max_length=300)

    @field_validator("city")
    @classmethod
    def check_city(cls, value: str) -> str:
        """Validate and sanitize the city name."""
        return validate_city_name(value)

    @field_validator("health_conditions")
    @classmethod
    def check_health_conditions(cls, values: list[str]) -> list[str]:
        """Sanitize and normalize health condition tags."""
        cleaned: list[str] = []
        for item in values[:10]:
            text = sanitize_text(item, max_length=40).lower()
            if text:
                cleaned.append(text)
        return cleaned

    @field_validator("lifestyle_notes")
    @classmethod
    def check_lifestyle_notes(cls, value: str) -> str:
        """Sanitize optional lifestyle context."""
        return sanitize_text(value, max_length=300)

    @property
    def is_sensitive_household(self) -> bool:
        """Return True if anyone in the household belongs to an AQI-sensitive group."""
        return self.has_children or self.has_elderly or len(self.health_conditions) > 0


class PollutantDetails(BaseModel):
    """Measured pollutant concentrations in µg/m³ (CO in mg/m³)."""

    pm25: float | None = Field(default=None, ge=0)
    pm10: float | None = Field(default=None, ge=0)
    o3: float | None = Field(default=None, ge=0)
    no2: float | None = Field(default=None, ge=0)
    so2: float | None = Field(default=None, ge=0)
    co: float | None = Field(default=None, ge=0)


class WeatherData(BaseModel):
    """Current meteorological snapshot relevant to smog dispersion."""

    temperature_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    wind_speed_kmh: float | None = Field(default=None, ge=0)
    condition: str = "Unknown"
    smog_trapping_risk: Literal["low", "moderate", "high"] = "moderate"
    dispersion_note: str = ""
    data_source: str = "open-meteo"


class HourlyTrendPoint(BaseModel):
    """Single hourly AQI/PM2.5 point for 24-hour diurnal smog visualization."""

    hour: str
    aqi: int = Field(ge=0, le=500)
    pm25: float = Field(ge=0.0)


class AQISnapshot(BaseModel):
    """Normalized real-time AQI snapshot returned by AQI endpoints and chat."""

    city: str
    resolved_city: str
    country: str = ""
    latitude: float | None = None
    longitude: float | None = None
    aqi: int = Field(ge=0, le=500)
    category: AQICategory
    category_label: str
    color: str
    text_color: str
    health_advisory: str
    dominant_pollutant: str = "pm25"
    pollutants: PollutantDetails
    weather: WeatherData
    hourly_trend: list[HourlyTrendPoint] = Field(default_factory=list)
    timestamp: str
    data_source: str
    cached: bool = False
