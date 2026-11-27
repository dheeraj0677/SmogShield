"""Sustainable low-emission lifestyle alternatives with quantified impact metrics."""

from models.enums import (
    CommuteType,
    CostLevel,
    DifficultyLevel,
    RecommendationCategory,
)
from models.schemas import AQISnapshot, RecommendationItem, UserProfile


def build_sustainable_alternatives(
    snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
) -> list[RecommendationItem]:
    """Provide low-emission lifestyle alternatives with clear CO2 & exposure savings."""
    items: list[RecommendationItem] = []

    if profile.commute_type in {CommuteType.CAR, CommuteType.MOTORBIKE}:
        items.append(
            RecommendationItem(
                id="alt-metro-carpool",
                category=RecommendationCategory.SUSTAINABLE_ALTERNATIVE,
                title="Swap solo vehicle commute for Metro/Bus or 3-person carpool",
                description=(
                    "For a typical 12 km urban round trip, switching from a solo petrol/diesel "
                    "vehicle to electric metro or a shared ride slashes tailpipe NOx and PM."
                ),
                impact=(
                    "Saves ~2.3 kg CO2 today and cuts personal roadside PM2.5 exposure by ~40% "
                    "compared to open-air riding or congested idling."
                ),
                impact_metric="2.3 kg CO2 saved | -40% PM2.5",
                co2_saved_kg=2.3,
                exposure_reduction_pct=40,
                difficulty=DifficultyLevel.MODERATE,
                cost=CostLevel.LOW,
                priority=1,
                best_time="Morning & evening commute",
                tags=["transit", "emissions", "commute"],
            )
        )

    if effective_aqi >= 201 and profile.commute_type != CommuteType.WORK_FROM_HOME:
        items.append(
            RecommendationItem(
                id="alt-remote-staggered",
                category=RecommendationCategory.SUSTAINABLE_ALTERNATIVE,
                title="Batch errands or request a Work-From-Home smog day",
                description=(
                    f"With AQI at {snapshot.aqi}, skipping one commute cuts fuel combustion "
                    "during peak inversion hours and keeps your household sheltered indoors."
                ),
                impact=(
                    "Eliminates 100% of commute tailpipe emissions (~2.8 kg CO2) and "
                    "transit smog exposure."
                ),
                impact_metric="2.8 kg CO2 saved | -75% transit exposure",
                co2_saved_kg=2.8,
                exposure_reduction_pct=75,
                difficulty=DifficultyLevel.MODERATE,
                cost=CostLevel.FREE,
                priority=1,
                best_time="Full workday",
                tags=["wfh", "trip-reduction"],
            )
        )

    if profile.commute_type == CommuteType.WALK_BIKE and effective_aqi > 150:
        items.append(
            RecommendationItem(
                id="alt-enclosed-transit",
                category=RecommendationCategory.SUSTAINABLE_ALTERNATIVE,
                title="Temporarily switch active walking/cycling to enclosed electric transit",
                description=(
                    "While cycling is green, heavy breathing at AQI >150 pulls 3–4x more PM2.5 "
                    "deep into lungs. Take enclosed AC metro/electric bus with an N95 today."
                ),
                impact=(
                    "Cuts inhaled particulate dose by ~65% while keeping per-passenger "
                    "emissions ultra-low."
                ),
                impact_metric="-65% inhaled PM2.5 dose",
                co2_saved_kg=0.9,
                exposure_reduction_pct=65,
                difficulty=DifficultyLevel.EASY,
                cost=CostLevel.LOW,
                priority=1,
                best_time="Commute hours",
                tags=["commute", "active-travel-protection"],
            )
        )

    items.append(
        RecommendationItem(
            id="alt-clean-heating-waste",
            category=RecommendationCategory.SUSTAINABLE_ALTERNATIVE,
            title="Adopt zero-burn neighborhood habits & clean electric warming",
            description=(
                "Avoid burning garden leaves, trash, or wood/coal braziers; compost dry leaves "
                "and layer warm thermal clothing instead of space-heating entire rooms."
            ),
            impact=(
                "One small backyard leaf/trash fire emits as much PM2.5 as dozens of cars. "
                "Zero-burn heating protects your immediate street microclimate."
            ),
            impact_metric="1.8 kg CO2 saved | Prevents local PM2.5 spike",
            co2_saved_kg=1.8,
            exposure_reduction_pct=30,
            difficulty=DifficultyLevel.EASY,
            cost=CostLevel.FREE,
            priority=2,
            best_time="Evening / night",
            tags=["zero-burn", "community", "heating"],
        )
    )

    items.append(
        RecommendationItem(
            id="alt-consolidated-deliveries",
            category=RecommendationCategory.SUSTAINABLE_ALTERNATIVE,
            title="Consolidate grocery & delivery orders to cut two-wheeler trips",
            description=(
                "Bundle weekly essentials into a single neighborhood pickup or consolidated "
                "slot instead of multiple urgent single-item courier rides."
            ),
            impact="Removes 3–4 short cold-start combustion trips per week from residential lanes.",
            impact_metric="1.1 kg CO2 saved per consolidated week",
            co2_saved_kg=1.1,
            exposure_reduction_pct=15,
            difficulty=DifficultyLevel.EASY,
            cost=CostLevel.FREE,
            priority=3,
            best_time="Midday off-peak",
            tags=["sustainable-living", "deliveries"],
        )
    )

    return items
