"""Hybrid rule-based + impact-quantified recommendation engine for SmogShield."""

from models.enums import (
    BudgetLevel,
    CommuteType,
    CostLevel,
    DifficultyLevel,
    HomeType,
    RecommendationCategory,
)
from models.schemas import (
    AQISnapshot,
    DailyScheduleSlot,
    RecommendationItem,
    RecommendationsResponse,
    UserProfile,
)
from utils.aqi_calculator import get_aqi_category, get_effective_aqi_for_profile


class RecommendationEngine:
    """Generates personalized routines, indoor air hacks, and sustainable alternatives."""

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

        daily_routine = self._build_daily_routine(aqi_snapshot, effective_aqi, profile)
        indoor_hacks = self._build_indoor_hacks(aqi_snapshot, effective_aqi, profile)
        alternatives = self._build_sustainable_alternatives(aqi_snapshot, effective_aqi, profile)
        health_protections = self._build_health_protections(effective_aqi, profile)
        schedule = self._build_schedule(aqi_snapshot, effective_aqi, profile)

        all_recs = daily_routine + indoor_hacks + alternatives + health_protections
        total_co2 = round(sum(item.co2_saved_kg for item in all_recs), 2)
        exposure_scores = [
            item.exposure_reduction_pct
            for item in all_recs
            if item.exposure_reduction_pct > 0
        ]
        # Combine top protections with diminishing returns rather than naive summation
        exposure_scores.sort(reverse=True)
        combined_exposure = 0.0
        for pct in exposure_scores[:4]:
            combined_exposure += (100.0 - combined_exposure) * (pct / 100.0)
        estimated_exposure = min(92, int(round(combined_exposure)))

        summary = self._build_personalization_summary(profile, effective_aqi, aqi_snapshot)

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
            personalization_summary=summary,
        )

    def _build_alert_message(
        self,
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

    def _build_daily_routine(
        self, snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
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
                    tags=[
                        "exercise",
                        "inversion",
                        "children" if profile.has_children else "fitness",
                    ],
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

    def _build_indoor_hacks(
        self, snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
    ) -> list[RecommendationItem]:
        """Generate practical indoor air quality hacks matched to home type and budget."""
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
                impact=(
                    "Prevents acute indoor NO2 and ultrafine oil aerosol peaks during meal prep."
                ),
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

    def _build_sustainable_alternatives(
        self, snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
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
                impact=(
                    "Removes 3–4 short cold-start combustion trips per week from "
                    "residential lanes."
                ),
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

    def _build_health_protections(
        self, effective_aqi: int, profile: UserProfile
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

    def _build_schedule(
        self, snapshot: AQISnapshot, effective_aqi: int, profile: UserProfile
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
            else (
                "Brief 15–20 min cross-ventilation if outdoor haze clears and wind >10 km/h."
            )
        )

        return [
            DailyScheduleSlot(
                time_window="6:00 AM – 9:30 AM",
                activity="Morning Routine & Commute",
                recommended_action=(
                    f"Indoor workout only; keep bedroom purifier running. {commute_action}"
                    if high_risk
                    else (
                        "Normal outdoor walk/commute; choose shaded parks away from major roads."
                    )
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

    @staticmethod
    def _build_personalization_summary(
        profile: UserProfile, effective_aqi: int, snapshot: AQISnapshot
    ) -> str:
        """Summarize which household parameters shaped the advice."""
        parts = [f"Location: {snapshot.resolved_city} (AQI {snapshot.aqi})"]
        parts.append(f"Household: {profile.family_members} member(s)")
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
