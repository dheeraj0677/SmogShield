"""Daily routine and health protection recommendation builders."""

from models.enums import (
    CostLevel,
    DifficultyLevel,
    RecommendationCategory,
)
from models.schemas import AQISnapshot, RecommendationItem, UserProfile


def build_daily_routine(
    snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
) -> list[RecommendationItem]:
    """Tailor daily activity timing to smog dispersion and family needs."""
    items: list[RecommendationItem] = []

    if effective_aqi <= 100:
        items.append(
            RecommendationItem(
                id="routine-ventilation-good",
                category=RecommendationCategory.DAILY_ROUTINE,
                title="Cross-ventilate home during midday breeze",
                description=(
                    "Open opposite windows for 20–30 minutes between 1:00 PM and 3:30 PM "
                    "when solar warmth lifts trapped surface pollutants."
                ),
                impact=(
                    "Flushes stale indoor CO2 and VOCs while ambient particulate levels "
                    "are lowest."
                ),
                impact_metric="-35% indoor CO2 buildup",
                co2_saved_kg=0.2,
                exposure_reduction_pct=15,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.FREE,
                priority=2,
                best_time="1:00 PM – 3:30 PM",
                tags=["ventilation", "routine"],
            )
        )
    else:
        items.append(
            RecommendationItem(
                id="routine-skip-morning-outdoor",
                category=RecommendationCategory.DAILY_ROUTINE,
                title="Shift morning outdoor exercise indoors",
                description=(
                    f"At AQI {snapshot.aqi} with {snapshot.weather.smog_trapping_risk} smog "
                    "trapping, early morning air (6–9 AM) holds dense cold-air inversion "
                    "PM2.5. Replace outdoor runs with 25 min indoor mobility or yoga."
                ),
                impact=(
                    "Avoids deep-lung PM2.5 deposition during peak breathing rate "
                    "(3–5x resting intake)."
                ),
                impact_metric="-65% peak exercise PM2.5 dose",
                co2_saved_kg=0.0,
                exposure_reduction_pct=55,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.FREE,
                priority=1,
                best_time="6:00 AM – 9:30 AM",
                tags=["exercise", "inversion", "children" if profile.has_children else "fitness"],
            )
        )

    if profile.has_children:
        items.append(
            RecommendationItem(
                id="routine-kids-indoor-play",
                category=RecommendationCategory.DAILY_ROUTINE,
                title="Plan low-dust indoor play & homework zone",
                description=(
                    "Keep children's afternoon play in a single filtered room away from "
                    "street-facing windows; schedule school drop-offs at gate time."
                ),
                impact=(
                    "Reduces children's cumulative daily PM2.5 inhalation during critical "
                    "lung development."
                ),
                impact_metric="-45% child particulate exposure",
                co2_saved_kg=0.3,
                exposure_reduction_pct=45,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.FREE,
                priority=1,
                best_time="3:30 PM – 6:30 PM",
                tags=["family", "children", "school"],
            )
        )

    if effective_aqi > 150:
        items.append(
            RecommendationItem(
                id="routine-sealed-rush-hour",
                category=RecommendationCategory.DAILY_ROUTINE,
                title="Lock down ventilation during rush-hour peaks",
                description=(
                    "Close street-facing windows and doors between 7–10 AM and 6–10 PM when "
                    "vehicle exhaust and biomass smoke spike simultaneously."
                ),
                impact=(
                    "Prevents outdoor NO2 and ultrafine soot plumes from infiltrating "
                    "living spaces."
                ),
                impact_metric="-35% indoor soot infiltration",
                co2_saved_kg=0.0,
                exposure_reduction_pct=35,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.FREE,
                priority=1,
                best_time="7:00–10:00 AM & 6:00–10:00 PM",
                tags=["ventilation", "rush-hour"],
            )
        )

    return items


def build_health_protections(
    effective_aqi: int, profile: UserProfile
) -> list[RecommendationItem]:
    """Personal health safeguards triggered by elevated AQI or vulnerable groups."""
    items: list[RecommendationItem] = []

    if effective_aqi >= 101:
        items.append(
            RecommendationItem(
                id="health-n95-mask",
                category=RecommendationCategory.HEALTH_PROTECTION,
                title="Wear a snug N95 / FFP2 / KN95 respirator outdoors",
                description=(
                    "Cloth and loose surgical masks let 60–80% of PM2.5 bypass around edges. "
                    "Pinch the nose bridge of a certified N95/FFP2 respirator for a tight seal."
                ),
                impact="Filters ≥95% of airborne PM2.5 particles when you must step outside.",
                impact_metric="-85% inhaled PM2.5 outdoors",
                co2_saved_kg=0.0,
                exposure_reduction_pct=85,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.LOW,
                priority=1,
                best_time="Whenever outdoors",
                tags=["mask", "n95", "protection"],
            )
        )

    if profile.health_conditions or profile.has_children or profile.has_elderly:
        items.append(
            RecommendationItem(
                id="health-action-plan",
                category=RecommendationCategory.HEALTH_PROTECTION,
                title="Keep rescue inhalers, saline nasal rinse & doctor action plan ready",
                description=(
                    "High PM2.5 and NO2 trigger delayed airway inflammation up to 24h later. "
                    "Keep inhalers handy and rinse nasal passages after outdoor trips."
                ),
                impact=(
                    "Clears trapped particulate irritants from upper airways and prevents "
                    "flare escalation."
                ),
                impact_metric="-30% upper-airway irritant load",
                co2_saved_kg=0.0,
                exposure_reduction_pct=25,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.FREE,
                priority=1,
                best_time="After returning indoors",
                tags=["asthma", "elderly", "children", "health"],
            )
        )

    return items
