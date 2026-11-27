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

    aqi_sources = ["open-meteo-live"]
    if settings.has_google_aqi:
        aqi_sources.insert(0, "google-air-quality")
    if settings.has_waqi:
        aqi_sources.insert(0, "waqi")

    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
        services={
            "llm": llm_status,
            "gemini": "configured" if settings.has_gemini else "fallback",
            "google_air_quality": "configured" if settings.has_google_aqi else "ready",
            "aqi": "+".join(aqi_sources),
            "weather": (
                "openweathermap+open-meteo"
                if settings.has_openweather
                else "open-meteo-live"
            ),
        },
    )
