"""Pydantic request and response schemas with strict validation."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from models.enums import (
    AQICategory,
    BudgetLevel,
    CommuteType,
    CostLevel,
    DifficultyLevel,
    HomeType,
    RecommendationCategory,
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
    """Measured pollutant concentrations in µg/m³ (CO in mg/m³ or µg/m³ normalized)."""

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
    timestamp: str
    data_source: str
    cached: bool = False


class RecommendationItem(BaseModel):
    """Actionable air quality recommendation with quantified direct impact."""

    id: str
    category: RecommendationCategory
    title: str
    description: str
    impact: str
    impact_metric: str
    co2_saved_kg: float = Field(default=0.0, ge=0.0)
    exposure_reduction_pct: int = Field(default=0, ge=0, le=95)
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    cost: CostLevel = CostLevel.FREE
    priority: int = Field(default=1, ge=1, le=5)
    best_time: str = "All day"
    tags: list[str] = Field(default_factory=list)


class DailyScheduleSlot(BaseModel):
    """Time-block entry in a smog-aware daily routine plan."""

    time_window: str
    activity: str
    recommended_action: str
    aqi_risk: Literal["low", "moderate", "high", "severe"]
    rationale: str
    impact: str


class RecommendationsResponse(BaseModel):
    """Full personalized recommendation package for a city and household profile."""

    city: str
    aqi_snapshot: AQISnapshot
    effective_aqi: int = Field(ge=0, le=500)
    alert_level: AQICategory
    alert_message: str
    daily_routine: list[RecommendationItem]
    indoor_hacks: list[RecommendationItem]
    alternatives: list[RecommendationItem]
    health_protections: list[RecommendationItem]
    schedule: list[DailyScheduleSlot]
    total_potential_co2_saved_kg: float = Field(ge=0.0)
    estimated_exposure_reduction_pct: int = Field(ge=0, le=95)
    personalization_summary: str


class ChatHistoryMessage(BaseModel):
    """Prior conversation turn passed from the client."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def check_content(cls, value: str) -> str:
        """Sanitize historical message content."""
        return sanitize_text(value, max_length=2000)


class ChatRequest(BaseModel):
    """Incoming conversational query to the SmogShield GenAI assistant."""

    message: str = Field(min_length=1, max_length=1500)
    city: str = Field(default="Delhi", min_length=2, max_length=80)
    user_profile: UserProfile | None = None
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=10)

    @field_validator("message")
    @classmethod
    def check_message(cls, value: str) -> str:
        """Sanitize user chat message and reject empty input after stripping."""
        cleaned = sanitize_text(value, max_length=1500)
        if not cleaned:
            raise ValueError("Message cannot be empty.")
        return cleaned

    @field_validator("city")
    @classmethod
    def check_city(cls, value: str) -> str:
        """Validate and sanitize requested city."""
        return validate_city_name(value)


class ChatResponse(BaseModel):
    """Conversational AI response accompanied by structured impact cards."""

    reply: str
    recommendations: list[RecommendationItem]
    aqi_snapshot: AQISnapshot
    impact_summary: str
    ai_provider: str
    follow_up_prompts: list[str]
    disclaimer: str = (
        "SmogShield provides environmental and lifestyle guidance only, not medical diagnoses. "
        "Consult a healthcare professional for respiratory or cardiovascular symptoms."
    )


class HealthCheckResponse(BaseModel):
    """Service liveness and capability status."""

    status: str
    version: str
    environment: str
    services: dict[str, str]
