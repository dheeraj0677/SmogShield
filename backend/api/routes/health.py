"""Health check endpoint."""

from fastapi import APIRouter, Request

from config import Settings
from models.schemas import HealthCheckResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request) -> HealthCheckResponse:
    """Return service liveness, version, and external API configuration status."""
    settings: Settings = request.app.state.settings
    if settings.has_openrouter:
        llm_status = f"openrouter ({settings.openrouter_model})"
    elif settings.has_gemini:
        llm_status = f"gemini ({settings.gemini_model})"
    else:
        llm_status = "rule-engine-fallback"

    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
        services={
            "llm": llm_status,
            "gemini": "configured" if settings.has_gemini else "fallback",
            "aqi": "waqi+open-meteo" if settings.has_waqi else "open-meteo-live",
            "weather": (
                "openweathermap+open-meteo"
                if settings.has_openweather
                else "open-meteo-live"
            ),
        },
    )
