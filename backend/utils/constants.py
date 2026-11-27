"""Domain constants: US EPA AQI breakpoints, category metadata, and pollutant info."""

from models.enums import AQICategory, PollutantType
from utils.city_baselines import CITY_FALLBACK_PROFILES

# 2024 US EPA PM2.5 and standard EPA breakpoints: (c_low, c_high, i_low, i_high)
EPA_BREAKPOINTS: dict[PollutantType, list[tuple[float, float, int, int]]] = {
    PollutantType.PM25: [
        (0.0, 9.0, 0, 50),
        (9.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 125.4, 151, 200),
        (125.5, 225.4, 201, 300),
        (225.5, 500.4, 301, 500),
    ],
    PollutantType.PM10: [
        (0.0, 54.0, 0, 50),
        (55.0, 154.0, 51, 100),
        (155.0, 254.0, 101, 150),
        (255.0, 354.0, 151, 200),
        (355.0, 424.0, 201, 300),
        (425.0, 604.0, 301, 500),
    ],
    PollutantType.O3: [
        (0.0, 106.0, 0, 50),
        (107.0, 137.0, 51, 100),
        (138.0, 167.0, 101, 150),
        (168.0, 206.0, 151, 200),
        (207.0, 392.0, 201, 300),
        (393.0, 784.0, 301, 500),
    ],
    PollutantType.NO2: [
        (0.0, 100.0, 0, 50),
        (101.0, 188.0, 51, 100),
        (189.0, 677.0, 101, 150),
        (678.0, 1220.0, 151, 200),
        (1221.0, 2348.0, 201, 300),
        (2349.0, 3850.0, 301, 500),
    ],
    PollutantType.SO2: [
        (0.0, 92.0, 0, 50),
        (93.0, 196.0, 51, 100),
        (197.0, 485.0, 101, 150),
        (486.0, 796.0, 151, 200),
        (797.0, 1582.0, 201, 300),
        (1583.0, 2630.0, 301, 500),
    ],
    PollutantType.CO: [
        (0.0, 5.0, 0, 50),
        (5.1, 10.8, 51, 100),
        (10.9, 14.3, 101, 150),
        (14.4, 17.7, 151, 200),
        (17.8, 34.9, 201, 300),
        (35.0, 58.0, 301, 500),
    ],
}

AQI_CATEGORY_META: dict[AQICategory, dict[str, str]] = {
    AQICategory.GOOD: {
        "label": "Good",
        "color": "#15803d",
        "text_color": "#ffffff",
        "advisory": (
            "Air quality is satisfactory. Ideal window for natural cross-ventilation "
            "and active outdoor routines."
        ),
    },
    AQICategory.MODERATE: {
        "label": "Moderate",
        "color": "#eab308",
        "text_color": "#0f172a",
        "advisory": (
            "Acceptable air quality for most, though unusually sensitive individuals "
            "should limit prolonged roadside exertion."
        ),
    },
    AQICategory.UNHEALTHY_SENSITIVE: {
        "label": "Unhealthy for Sensitive Groups",
        "color": "#ea580c",
        "text_color": "#ffffff",
        "advisory": (
            "Children, older adults, and people with asthma or heart disease should "
            "reduce outdoor exertion and wear N95 protection near traffic."
        ),
    },
    AQICategory.UNHEALTHY: {
        "label": "Unhealthy",
        "color": "#dc2626",
        "text_color": "#ffffff",
        "advisory": (
            "Everyone may experience respiratory irritation. Keep windows sealed during "
            "peak traffic and shift workouts indoors."
        ),
    },
    AQICategory.VERY_UNHEALTHY: {
        "label": "Very Unhealthy",
        "color": "#7e22ce",
        "text_color": "#ffffff",
        "advisory": (
            "Health alert: high risk for all families. Stay indoors with filtered air, "
            "seal window drafts, and avoid non-essential travel."
        ),
    },
    AQICategory.HAZARDOUS: {
        "label": "Hazardous",
        "color": "#881337",
        "text_color": "#ffffff",
        "advisory": (
            "Emergency winter smog conditions. Remain indoors with active HEPA/DIY filtration, "
            "wear a tight-fitting N95/FFP2 if travel is unavoidable, and work/study from home."
        ),
    },
}

POLLUTANT_INFO: dict[str, dict[str, str]] = {
    "pm25": {
        "name": "PM2.5",
        "unit": "µg/m³",
        "description": (
            "Fine particulate matter (≤2.5 µm) that penetrates deep into lungs and bloodstream."
        ),
    },
    "pm10": {
        "name": "PM10",
        "unit": "µg/m³",
        "description": (
            "Coarse dust and smoke particles (≤10 µm) causing airway and eye irritation."
        ),
    },
    "o3": {
        "name": "Ozone (O₃)",
        "unit": "µg/m³",
        "description": (
            "Ground-level photochemical smog formed in sunlight from vehicle & industrial fumes."
        ),
    },
    "no2": {
        "name": "NO₂",
        "unit": "µg/m³",
        "description": (
            "Traffic and combustion gas linked to asthma flare-ups and airway inflammation."
        ),
    },
    "so2": {
        "name": "SO₂",
        "unit": "µg/m³",
        "description": (
            "Sulfur dioxide from coal/diesel combustion contributing to haze and bronchospasm."
        ),
    },
    "co": {
        "name": "CO",
        "unit": "mg/m³",
        "description": "Carbon monoxide from incomplete fuel burning and indoor unvented heaters.",
    },
}

__all__ = [
    "AQI_CATEGORY_META",
    "CITY_FALLBACK_PROFILES",
    "EPA_BREAKPOINTS",
    "POLLUTANT_INFO",
]
