"""Health check endpoint."""

from fastapi import APIRouter, Request

from config import Settings
from models.schemas import HealthCheckResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request) -> HealthCheckResponse:
    """Return service liveness, version, and external API configuration status."""
    settings: Settings = request.app.state.settings
    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
        services={
            "gemini": "configured" if settings.has_gemini else "rule-engine-fallback",
            "aqi": "waqi+open-meteo" if settings.has_waqi else "open-meteo-live",
            "weather": (
                "openweathermap+open-meteo"
                if settings.has_openweather
                else "open-meteo-live"
            ),
        },
    )
