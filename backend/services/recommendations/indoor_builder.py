"""Indoor air quality hack builders tailored to purifier ownership and budget."""

from models.enums import (
    BudgetLevel,
    CostLevel,
    DifficultyLevel,
    HomeType,
    RecommendationCategory,
)
from models.schemas import AQISnapshot, RecommendationItem, UserProfile


def build_indoor_hacks(
    snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
) -> list[RecommendationItem]:
    """Generate practical indoor air quality hacks matched to home type and budget."""
    del snapshot
    items: list[RecommendationItem] = []

    if not profile.has_air_purifier:
        if profile.budget == BudgetLevel.LOW:
            items.append(
                RecommendationItem(
                    id="indoor-diy-box-fan",
                    category=RecommendationCategory.INDOOR_HACK,
                    title="Build a DIY Box-Fan + MERV-13/HEPA Filter (Corsi-Rosenthal)",
                    description=(
                        "Tape a MERV-13 or replacement HEPA filter securely to the intake "
                        "side of a standard box/pedestal fan using painter's tape."
                    ),
                    impact=(
                        "Captures 50–65% of indoor PM2.5 in a bedroom at 1/5th the cost "
                        "of commercial purifiers."
                    ),
                    impact_metric="-55% indoor PM2.5",
                    co2_saved_kg=0.4,
                    exposure_reduction_pct=55,
                    difficulty=DifficultyLevel.MODERATE,
                    cost=CostLevel.LOW,
                    priority=1,
                    best_time="Run continuously in bedroom",
                    tags=["diy", "hepa", "low-budget"],
                )
            )
        else:
            items.append(
                RecommendationItem(
                    id="indoor-true-hepa-zone",
                    category=RecommendationCategory.INDOOR_HACK,
                    title="Create a single 'Clean Air Sanctuary' bedroom with True HEPA",
                    description=(
                        "Place a True HEPA (H13) purifier in the primary sleeping room, "
                        "keep the door shut, and run it overnight (avoid ionizer modes)."
                    ),
                    impact=(
                        "Gives lungs 8+ hours of <15 µg/m³ recovery air every night, "
                        "cutting airway inflammation."
                    ),
                    impact_metric="-70% bedroom PM2.5 overnight",
                    co2_saved_kg=0.0,
                    exposure_reduction_pct=65,
                    difficulty=DifficultyLevel.EASY,
                    cost=CostLevel.MEDIUM,
                    priority=1,
                    best_time="Overnight (9:00 PM – 7:00 AM)",
                    tags=["hepa", "sleep", "clean-room"],
                )
            )
    else:
        items.append(
            RecommendationItem(
                id="indoor-optimize-purifier",
                category=RecommendationCategory.INDOOR_HACK,
                title="Optimize existing air purifier placement & pre-filter hygiene",
                description=(
                    "Keep your purifier 30 cm away from walls, vacuum the washable mesh "
                    "pre-filter weekly, and run it in the occupied room."
                ),
                impact=(
                    "Boosts Clean Air Delivery Rate (CADR) efficiency by ~25% without "
                    "extra electricity."
                ),
                impact_metric="+25% CADR efficiency",
                co2_saved_kg=0.3,
                exposure_reduction_pct=45,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.FREE,
                priority=1,
                best_time="All day when room occupied",
                tags=["air-purifier", "maintenance"],
            )
        )

    items.append(
        RecommendationItem(
            id="indoor-wet-mopping",
            category=RecommendationCategory.INDOOR_HACK,
            title="Switch from dry sweeping/dusting to damp microfiber mopping",
            description=(
                "Settled PM2.5 and coarse dust re-aerosolize for hours after dry brooming. "
                "Use a damp mop and damp cloth on floors and window sills once daily."
            ),
            impact="Eliminates dust resuspension spikes that can double indoor PM10 levels.",
            impact_metric="-40% resuspended indoor dust",
            co2_saved_kg=0.0,
            exposure_reduction_pct=30,
            difficulty=DifficultyLevel.EASY,
            cost=CostLevel.FREE,
            priority=2,
            best_time="Late morning",
            tags=["cleaning", "dust-control"],
        )
    )

    items.append(
        RecommendationItem(
            id="indoor-kitchen-exhaust",
            category=RecommendationCategory.INDOOR_HACK,
            title="Use lids, induction/pressure cooking, and kitchen exhaust",
            description=(
                "High-heat frying and gas combustion spike indoor PM2.5 above 300 µg/m³. "
                "Cover pans, run the chimney/exhaust fan, and avoid incense or candles indoors."
            ),
            impact="Prevents acute indoor NO2 and ultrafine oil aerosol peaks during meal prep.",
            impact_metric="-60% cooking PM2.5 spike",
            co2_saved_kg=0.5,
            exposure_reduction_pct=40,
            difficulty=DifficultyLevel.EASY,
            cost=CostLevel.FREE,
            priority=1 if effective_aqi > 150 else 2,
            best_time="During meal preparation",
            tags=["cooking", "indoor-sources"],
        )
    )

    if effective_aqi >= 151:
        draft_note = (
            "Seal sliding balcony tracks and main door bottoms with foam weatherstripping "
            "or rolled damp towels during dense smog episodes."
            if profile.home_type == HomeType.APARTMENT
            else (
                "Seal exterior door thresholds and unused chimney/exhaust vents "
                "with weatherstripping."
            )
        )
        items.append(
            RecommendationItem(
                id="indoor-seal-drafts",
                category=RecommendationCategory.INDOOR_HACK,
                title="Seal window & door gaps against smog infiltration",
                description=draft_note,
                impact="Cuts unconditioned outdoor smog seepage by up to 35% in leaky rooms.",
                impact_metric="-35% smog seepage",
                co2_saved_kg=0.6,
                exposure_reduction_pct=35,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.LOW,
                priority=2,
                best_time="Before evening smog surge",
                tags=["weatherproofing", "sealing"],
            )
        )

    return items
