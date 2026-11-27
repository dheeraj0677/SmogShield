"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _parse_csv(raw_value: str) -> list[str]:
    """Parse a comma-separated environment string into a clean list."""
    return [item.strip() for item in raw_value.split(",") if item.strip()]


class Settings(BaseModel):
    """Typed runtime settings for the SmogShield backend."""

    app_name: str = "SmogShield API"
    app_version: str = "1.0.0"
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())
    gemini_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
    )
    openrouter_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY", "").strip()
    )
    openrouter_model: str = Field(
        default_factory=lambda: os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()
    )
    waqi_api_token: str = Field(default_factory=lambda: os.getenv("WAQI_API_TOKEN", "").strip())
    google_air_quality_api_key: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_AIR_QUALITY_API_KEY", "").strip()
    )
    openweather_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENWEATHER_API_KEY", "").strip()
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: _parse_csv(
            os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        )
    )
    cache_ttl_seconds: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_SECONDS", "900"))
    )
    cache_max_entries: int = 256
    rate_limit_chat_per_min: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_CHAT_PER_MIN", "30"))
    )
    rate_limit_aqi_per_min: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_AQI_PER_MIN", "60"))
    )
    request_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10.0"))
    )

    @property
    def has_gemini(self) -> bool:
        """Return True when a Gemini API key is configured."""
        return bool(self.gemini_api_key)

    @property
    def has_openrouter(self) -> bool:
        """Return True when an OpenRouter API key is configured."""
        return bool(self.openrouter_api_key)

    @property
    def has_waqi(self) -> bool:
        """Return True when a WAQI API token is configured."""
        return bool(self.waqi_api_token)

    @property
    def has_google_aqi(self) -> bool:
        """Return True when a Google Air Quality API key is configured."""
        return bool(self.google_air_quality_api_key)

    @property
    def has_openweather(self) -> bool:
        """Return True when an OpenWeatherMap key is configured."""
        return bool(self.openweather_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
