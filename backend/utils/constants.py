"""Domain constants: US EPA AQI breakpoints, category metadata, and fallback profiles."""

from models.enums import AQICategory, PollutantType

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
    # O3 breakpoints in µg/m³ (converted from 8-hr ppb * 1.96)
    PollutantType.O3: [
        (0.0, 106.0, 0, 50),
        (107.0, 137.0, 51, 100),
        (138.0, 167.0, 101, 150),
        (168.0, 206.0, 151, 200),
        (207.0, 392.0, 201, 300),
        (393.0, 784.0, 301, 500),
    ],
    # NO2 breakpoints in µg/m³ (1-hr ppb * 1.88)
    PollutantType.NO2: [
        (0.0, 100.0, 0, 50),
        (101.0, 188.0, 51, 100),
        (189.0, 677.0, 101, 150),
        (678.0, 1220.0, 151, 200),
        (1221.0, 2348.0, 201, 300),
        (2349.0, 3850.0, 301, 500),
    ],
    # SO2 breakpoints in µg/m³ (1-hr ppb * 2.62)
    PollutantType.SO2: [
        (0.0, 92.0, 0, 50),
        (93.0, 196.0, 51, 100),
        (197.0, 485.0, 101, 150),
        (486.0, 796.0, 151, 200),
        (797.0, 1582.0, 201, 300),
        (1583.0, 2630.0, 301, 500),
    ],
    # CO breakpoints in mg/m³ (8-hr ppm * 1.15)
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

# Offline resilience baselines for major cities when live external APIs are unreachable
CITY_FALLBACK_PROFILES: dict[str, dict] = {
    "delhi": {
        "resolved_city": "Delhi",
        "country": "India",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "pm25": 178.0,
        "pm10": 265.0,
        "o3": 42.0,
        "no2": 68.0,
        "so2": 18.0,
        "co": 2.4,
        "temp_c": 14.5,
        "humidity": 74.0,
        "wind_kmh": 5.2,
        "condition": "Dense Winter Haze",
    },
    "lahore": {
        "resolved_city": "Lahore",
        "country": "Pakistan",
        "latitude": 31.5204,
        "longitude": 74.3587,
        "pm25": 195.0,
        "pm10": 290.0,
        "o3": 38.0,
        "no2": 72.0,
        "so2": 21.0,
        "co": 2.6,
        "temp_c": 13.8,
        "humidity": 78.0,
        "wind_kmh": 4.1,
        "condition": "Severe Winter Smog",
    },
    "beijing": {
        "resolved_city": "Beijing",
        "country": "China",
        "latitude": 39.9042,
        "longitude": 116.4074,
        "pm25": 68.0,
        "pm10": 105.0,
        "o3": 50.0,
        "no2": 46.0,
        "so2": 11.0,
        "co": 1.1,
        "temp_c": 5.0,
        "humidity": 48.0,
        "wind_kmh": 9.5,
        "condition": "Light Urban Haze",
    },
    "mumbai": {
        "resolved_city": "Mumbai",
        "country": "India",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "pm25": 62.0,
        "pm10": 118.0,
        "o3": 54.0,
        "no2": 44.0,
        "so2": 14.0,
        "co": 1.2,
        "temp_c": 26.5,
        "humidity": 65.0,
        "wind_kmh": 12.0,
        "condition": "Coastal Haze",
    },
    "kolkata": {
        "resolved_city": "Kolkata",
        "country": "India",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "pm25": 115.0,
        "pm10": 172.0,
        "o3": 45.0,
        "no2": 58.0,
        "so2": 16.0,
        "co": 1.7,
        "temp_c": 19.5,
        "humidity": 70.0,
        "wind_kmh": 6.8,
        "condition": "Misty Smog",
    },
    "dhaka": {
        "resolved_city": "Dhaka",
        "country": "Bangladesh",
        "latitude": 23.8103,
        "longitude": 90.4125,
        "pm25": 142.0,
        "pm10": 215.0,
        "o3": 41.0,
        "no2": 62.0,
        "so2": 19.0,
        "co": 2.0,
        "temp_c": 18.2,
        "humidity": 72.0,
        "wind_kmh": 5.5,
        "condition": "Winter Haze",
    },
    "kathmandu": {
        "resolved_city": "Kathmandu",
        "country": "Nepal",
        "latitude": 27.7172,
        "longitude": 85.3240,
        "pm25": 98.0,
        "pm10": 148.0,
        "o3": 44.0,
        "no2": 39.0,
        "so2": 10.0,
        "co": 1.4,
        "temp_c": 11.5,
        "humidity": 68.0,
        "wind_kmh": 4.8,
        "condition": "Valley Inversion Haze",
    },
    "london": {
        "resolved_city": "London",
        "country": "United Kingdom",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "pm25": 14.0,
        "pm10": 24.0,
        "o3": 58.0,
        "no2": 29.0,
        "so2": 4.0,
        "co": 0.4,
        "temp_c": 8.2,
        "humidity": 76.0,
        "wind_kmh": 17.5,
        "condition": "Partly Cloudy",
    },
    "new york": {
        "resolved_city": "New York",
        "country": "United States",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "pm25": 11.5,
        "pm10": 22.0,
        "o3": 62.0,
        "no2": 26.0,
        "so2": 3.5,
        "co": 0.4,
        "temp_c": 7.5,
        "humidity": 58.0,
        "wind_kmh": 15.2,
        "condition": "Clear & Crisp",
    },
    "los angeles": {
        "resolved_city": "Los Angeles",
        "country": "United States",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "pm25": 24.0,
        "pm10": 46.0,
        "o3": 98.0,
        "no2": 41.0,
        "so2": 5.0,
        "co": 0.7,
        "temp_c": 18.0,
        "humidity": 52.0,
        "wind_kmh": 10.5,
        "condition": "Sunny Haze",
    },
    "bengaluru": {
        "resolved_city": "Bengaluru",
        "country": "India",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "pm25": 31.0,
        "pm10": 58.0,
        "o3": 48.0,
        "no2": 34.0,
        "so2": 7.5,
        "co": 0.8,
        "temp_c": 22.0,
        "humidity": 61.0,
        "wind_kmh": 11.0,
        "condition": "Mild Breeze",
    },
    "lucknow": {
        "resolved_city": "Lucknow",
        "country": "India",
        "latitude": 26.8467,
        "longitude": 80.9462,
        "pm25": 162.0,
        "pm10": 238.0,
        "o3": 40.0,
        "no2": 60.0,
        "so2": 15.0,
        "co": 2.1,
        "temp_c": 14.0,
        "humidity": 76.0,
        "wind_kmh": 4.9,
        "condition": "Winter Fog & Smog",
    },
}
