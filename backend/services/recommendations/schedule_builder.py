"""Smog-aware morning-to-night daily schedule builder."""

from models.enums import CommuteType
from models.schemas import AQISnapshot, DailyScheduleSlot, UserProfile


def build_schedule(
    snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
) -> list[DailyScheduleSlot]:
    """Produce a practical morning-to-night smog-aware schedule."""
    high_risk = effective_aqi >= 151
    severe_risk = effective_aqi >= 201
    morning_risk = "severe" if severe_risk else ("high" if high_risk else "moderate")
    midday_risk = "high" if severe_risk else ("moderate" if high_risk else "low")
    evening_risk = "severe" if effective_aqi >= 180 else ("high" if high_risk else "moderate")

    commute_action = (
        "Work from home if possible; otherwise use enclosed metro/AC transit with an N95 mask."
        if high_risk and profile.commute_type != CommuteType.WORK_FROM_HOME
        else "Run errands or commute via public transit/carpool along lower-traffic routes."
    )
    midday_action = (
        "Keep windows closed and run HEPA/DIY filter; do light indoor stretching."
        if severe_risk
        else "Brief 15–20 min cross-ventilation if outdoor haze clears and wind >10 km/h."
    )

    return [
        DailyScheduleSlot(
            time_window="6:00 AM – 9:30 AM",
            activity="Morning Routine & Commute",
            recommended_action=(
                f"Indoor workout only; keep bedroom purifier running. {commute_action}"
                if high_risk
                else "Normal outdoor walk/commute; choose shaded parks away from major roads."
            ),
            aqi_risk=morning_risk,  # type: ignore[arg-type]
            rationale=(
                "Cold morning air traps overnight vehicle and heating soot near ground level."
            ),
            impact="Cuts peak morning particulate inhalation by 45–65%.",
        ),
        DailyScheduleSlot(
            time_window="12:30 PM – 3:30 PM",
            activity="Midday Reset & Ventilation",
            recommended_action=midday_action,
            aqi_risk=midday_risk,  # type: ignore[arg-type]
            rationale=(
                f"Solar heating lifts the mixing layer; current wind is "
                f"{snapshot.weather.wind_speed_kmh or 'light'} km/h."
            ),
            impact="Refreshes indoor oxygen while minimizing particulate ingress.",
        ),
        DailyScheduleSlot(
            time_window="5:30 PM – 9:30 PM",
            activity="Evening Rush & Dinner Prep",
            recommended_action=(
                "Seal windows, switch kitchen exhaust ON while cooking, and keep kids indoors."
                if effective_aqi >= 101
                else "Use kitchen exhaust while cooking; moderate outdoor play allowed."
            ),
            aqi_risk=evening_risk,  # type: ignore[arg-type]
            rationale=(
                "Evening temperature drop + rush-hour exhaust + cooking spikes PM2.5 rapidly."
            ),
            impact="Prevents indoor PM2.5 buildup above hazardous thresholds.",
        ),
        DailyScheduleSlot(
            time_window="9:30 PM – 6:00 AM",
            activity="Overnight Clean-Air Sleep",
            recommended_action=(
                "Close bedroom door, run HEPA/DIY fan filter on low-medium, "
                "and avoid scented candles."
            ),
            aqi_risk="moderate" if effective_aqi < 151 else "high",
            rationale=(
                "8 hours of clean sleep lowers overnight cardiovascular & respiratory stress."
            ),
            impact="Reduces overnight fine-particle exposure by up to 65%.",
        ),
    ]
