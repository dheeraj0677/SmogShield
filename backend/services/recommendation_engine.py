"""Hybrid rule-based + impact-quantified recommendation engine facade."""

from models.schemas import (
    AQISnapshot,
    RecommendationsResponse,
    UserProfile,
)
from services.recommendations.alternatives_builder import build_sustainable_alternatives
from services.recommendations.indoor_builder import build_indoor_hacks
from services.recommendations.routine_builder import (
    build_daily_routine,
    build_health_protections,
)
from services.recommendations.schedule_builder import build_schedule
from utils.aqi_calculator import get_aqi_category, get_effective_aqi_for_profile


class RecommendationEngine:
    """Orchestrates personalized routines, indoor air hacks, and sustainable alternatives."""

    def generate(
        self, aqi_snapshot: AQISnapshot, user_profile: UserProfile | None = None
    ) -> RecommendationsResponse:
        """Build a full recommendation suite tailored to live AQI, weather, and household."""
        profile = user_profile or UserProfile(city=aqi_snapshot.resolved_city)
        effective_aqi = get_effective_aqi_for_profile(aqi_snapshot.aqi, profile)
        alert_level, alert_label, _, _, base_advisory = get_aqi_category(effective_aqi)

        alert_message = self._build_alert_message(
            aqi_snapshot=aqi_snapshot,
            effective_aqi=effective_aqi,
            alert_label=alert_label,
            base_advisory=base_advisory,
            profile=profile,
        )

        daily_routine = build_daily_routine(aqi_snapshot, effective_aqi, profile)
        indoor_hacks = build_indoor_hacks(aqi_snapshot, effective_aqi, profile)
        alternatives = build_sustainable_alternatives(aqi_snapshot, effective_aqi, profile)
        health_protections = build_health_protections(effective_aqi, profile)
        schedule = build_schedule(aqi_snapshot, effective_aqi, profile)

        all_recs = daily_routine + indoor_hacks + alternatives + health_protections
        total_co2 = round(sum(item.co2_saved_kg for item in all_recs), 2)
        exposure_scores = sorted(
            [item.exposure_reduction_pct for item in all_recs if item.exposure_reduction_pct > 0],
            reverse=True,
        )
        combined_exposure = 0.0
        for pct in exposure_scores[:4]:
            combined_exposure += (100.0 - combined_exposure) * (pct / 100.0)
        estimated_exposure = min(92, int(round(combined_exposure)))

        return RecommendationsResponse(
            city=aqi_snapshot.resolved_city,
            aqi_snapshot=aqi_snapshot,
            effective_aqi=effective_aqi,
            alert_level=alert_level,
            alert_message=alert_message,
            daily_routine=daily_routine,
            indoor_hacks=indoor_hacks,
            alternatives=alternatives,
            health_protections=health_protections,
            schedule=schedule,
            total_potential_co2_saved_kg=total_co2,
            estimated_exposure_reduction_pct=estimated_exposure,
            personalization_summary=self._build_personalization_summary(
                profile, effective_aqi, aqi_snapshot
            ),
        )

    @staticmethod
    def _build_alert_message(
        aqi_snapshot: AQISnapshot,
        effective_aqi: int,
        alert_label: str,
        base_advisory: str,
        profile: UserProfile,
    ) -> str:
        """Construct a clear, household-specific risk alert."""
        if effective_aqi > aqi_snapshot.aqi and profile.is_sensitive_household:
            groups = []
            if profile.has_children:
                groups.append("children")
            if profile.has_elderly:
                groups.append("older adults")
            if profile.health_conditions:
                groups.append(", ".join(profile.health_conditions))
            group_str = " & ".join(groups) if groups else "sensitive members"
            return (
                f"Live AQI is {aqi_snapshot.aqi} ({aqi_snapshot.category_label}), which carries "
                f"an effective risk equivalent of AQI {effective_aqi} ({alert_label}) for your "
                f"household ({group_str}). {base_advisory}"
            )
        return (
            f"Live AQI in {aqi_snapshot.resolved_city} is "
            f"{aqi_snapshot.aqi} ({alert_label}). {base_advisory}"
        )

    @staticmethod
    def _build_personalization_summary(
        profile: UserProfile, effective_aqi: int, snapshot: AQISnapshot
    ) -> str:
        """Summarize which household parameters shaped the advice."""
        parts = [
            f"Location: {snapshot.resolved_city} (AQI {snapshot.aqi})",
            f"Household: {profile.family_members} member(s)",
        ]
        if profile.has_children:
            parts.append("children present")
        if profile.has_elderly:
            parts.append("elderly present")
        if profile.health_conditions:
            parts.append(f"conditions: {', '.join(profile.health_conditions)}")
        parts.append(f"commute: {profile.commute_type.value.replace('_', ' ')}")
        parts.append(f"budget: {profile.budget.value}")
        if effective_aqi != snapshot.aqi:
            parts.append(f"sensitivity-adjusted AQI: {effective_aqi}")
        return " | ".join(parts)
