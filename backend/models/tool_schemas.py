"""Engineering solver schemas (CADR calculator & clean-corridor commute planner)."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from utils.validators import validate_city_name


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
