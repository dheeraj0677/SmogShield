"""Enumerations for air quality categories, pollutants, and user preferences."""

from enum import Enum


class AQICategory(str, Enum):
    """US EPA Air Quality Index categories."""

    GOOD = "good"
    MODERATE = "moderate"
    UNHEALTHY_SENSITIVE = "unhealthy_sensitive"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very_unhealthy"
    HAZARDOUS = "hazardous"


class PollutantType(str, Enum):
    """Supported ambient air pollutants."""

    PM25 = "pm25"
    PM10 = "pm10"
    O3 = "o3"
    NO2 = "no2"
    SO2 = "so2"
    CO = "co"


class RecommendationCategory(str, Enum):
    """Categorization of personalized SmogShield advice."""

    DAILY_ROUTINE = "daily_routine"
    INDOOR_HACK = "indoor_hack"
    SUSTAINABLE_ALTERNATIVE = "sustainable_alternative"
    HEALTH_PROTECTION = "health_protection"


class DifficultyLevel(str, Enum):
    """Effort required to act on a recommendation."""

    EASY = "easy"
    MODERATE = "moderate"
    ADVANCED = "advanced"


class CostLevel(str, Enum):
    """Estimated out-of-pocket cost of a recommendation."""

    FREE = "free"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CommuteType(str, Enum):
    """Primary user commute mode."""

    CAR = "car"
    MOTORBIKE = "motorbike"
    PUBLIC_TRANSIT = "public_transit"
    WALK_BIKE = "walk_bike"
    WORK_FROM_HOME = "work_from_home"


class HomeType(str, Enum):
    """User household dwelling type."""

    APARTMENT = "apartment"
    INDEPENDENT_HOUSE = "independent_house"
    SHARED_HOUSING = "shared_housing"


class BudgetLevel(str, Enum):
    """User budget preference for air-quality interventions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
