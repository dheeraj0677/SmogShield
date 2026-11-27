"""US EPA Air Quality Index calculation and household sensitivity helpers."""

from models.enums import AQICategory, PollutantType
from models.schemas import PollutantDetails, UserProfile
from utils.constants import AQI_CATEGORY_META, EPA_BREAKPOINTS


def calculate_sub_index(pollutant: PollutantType, concentration: float | None) -> int | None:
    """Calculate the US EPA AQI sub-index for a single pollutant concentration."""
    if concentration is None or concentration < 0:
        return None

    breakpoints = EPA_BREAKPOINTS.get(pollutant)
    if not breakpoints:
        return None

    # Truncate concentration to match EPA breakpoint precision
    value = round(concentration, 1)
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= value <= c_high:
            sub_index = ((i_high - i_low) / (c_high - c_low)) * (value - c_low) + i_low
            return int(round(sub_index))

    # Exceeds top breakpoint -> cap at 500
    if value > breakpoints[-1][1]:
        return 500
    return 0


def calculate_overall_aqi(pollutants: PollutantDetails) -> tuple[int, str]:
    """Compute overall AQI and dominant pollutant across all available measurements."""
    sub_indices: dict[str, int] = {}
    pollutant_map = {
        PollutantType.PM25: pollutants.pm25,
        PollutantType.PM10: pollutants.pm10,
        PollutantType.O3: pollutants.o3,
        PollutantType.NO2: pollutants.no2,
        PollutantType.SO2: pollutants.so2,
        PollutantType.CO: pollutants.co,
    }
    for p_type, conc in pollutant_map.items():
        idx = calculate_sub_index(p_type, conc)
        if idx is not None:
            sub_indices[p_type.value] = idx

    if not sub_indices:
        return 50, "pm25"

    dominant = max(sub_indices, key=lambda key: sub_indices[key])
    return min(500, max(0, sub_indices[dominant])), dominant


def get_aqi_category(aqi: int) -> tuple[AQICategory, str, str, str, str]:
    """Return (category, label, bg_color, text_color, advisory) for a given AQI value."""
    clamped = max(0, min(500, aqi))
    if clamped <= 50:
        category = AQICategory.GOOD
    elif clamped <= 100:
        category = AQICategory.MODERATE
    elif clamped <= 150:
        category = AQICategory.UNHEALTHY_SENSITIVE
    elif clamped <= 200:
        category = AQICategory.UNHEALTHY
    elif clamped <= 300:
        category = AQICategory.VERY_UNHEALTHY
    else:
        category = AQICategory.HAZARDOUS

    meta = AQI_CATEGORY_META[category]
    return (
        category,
        meta["label"],
        meta["color"],
        meta["text_color"],
        meta["advisory"],
    )


def get_effective_aqi_for_profile(aqi: int, user_profile: UserProfile | None) -> int:
    """Shift risk posture upward for households with asthma, COPD, children, or elderly."""
    if user_profile is None or not user_profile.is_sensitive_household:
        return aqi

    shift = 0
    conditions = set(user_profile.health_conditions)
    if conditions & {"asthma", "copd", "heart_disease", "respiratory", "pregnancy"}:
        shift += 40
    elif conditions:
        shift += 25

    if user_profile.has_children or user_profile.has_elderly:
        shift += 20

    return min(500, aqi + shift)
