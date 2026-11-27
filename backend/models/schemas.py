"""Recommendations, chat, health, and solver Pydantic schemas."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from models.aqi_schemas import (
    AQISnapshot,
    HourlyTrendPoint,
    PollutantDetails,
    UserProfile,
    WeatherData,
)
from models.enums import (
    AQICategory,
    CostLevel,
    DifficultyLevel,
    RecommendationCategory,
)
from models.tool_schemas import (
    CADRRequest,
    CADRResponse,
    CommuteModeOption,
    CommutePlanRequest,
    CommutePlanResponse,
)
from utils.validators import sanitize_text, validate_city_name


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


__all__ = [
    "AQISnapshot",
    "CADRRequest",
    "CADRResponse",
    "ChatHistoryMessage",
    "ChatRequest",
    "ChatResponse",
    "CommuteModeOption",
    "CommutePlanRequest",
    "CommutePlanResponse",
    "DailyScheduleSlot",
    "HealthCheckResponse",
    "HourlyTrendPoint",
    "PollutantDetails",
    "RecommendationItem",
    "RecommendationsResponse",
    "UserProfile",
    "WeatherData",
]
