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


class CADRRequest(BaseModel):
    """Parameters for room-level Clean Air Delivery Rate calculation."""

    room_area_sqft: float = Field(default=160.0, ge=40.0, le=2500.0)
    ceiling_height_ft: float = Field(default=9.5, ge=7.0, le=20.0)
    outdoor_pm25: float = Field(default=150.0, ge=1.0, le=900.0)
    purifier_cadr_m3h: float = Field(default=250.0, ge=20.0, le=2000.0)
    seal_quality: Literal["tight", "average", "leaky"] = "average"


class CADRResponse(BaseModel):
    """Calculated indoor ACH and decay timeline."""

    room_volume_m3: float
    ach: float
    recommended_cadr_m3h: float
    initial_indoor_pm25: float
    projected_steady_pm25: float
    minutes_to_safe_air: int
    meets_target_ach: bool
    efficiency_note: str


class CommutePlanRequest(BaseModel):
    """Request for clean-corridor Dijkstra routing and modal dose comparison."""

    city: str = Field(default="Delhi", min_length=2, max_length=80)
    distance_km: float = Field(default=8.0, ge=1.0, le=80.0)
    wear_n95_mask: bool = False

    @field_validator("city")
    @classmethod
    def check_city(cls, value: str) -> str:
        """Validate and sanitize requested city."""
        return validate_city_name(value)


class CommuteModeOption(BaseModel):
    """Inhaled dose and carbon metrics for a single travel mode."""

    mode: str
    label: str
    duration_min: int
    inhaled_pm25_ug: float
    co2_kg: float
    exposure_vs_peak_pct: int
    recommended: bool


class CommutePlanResponse(BaseModel):
    """Combined clean-corridor pathfinder and modal exposure table."""

    city: str
    ambient_aqi: int
    ambient_pm25: float
    corridor_analysis: dict
    mode_comparisons: list[CommuteModeOption]
