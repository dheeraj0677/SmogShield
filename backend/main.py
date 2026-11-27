"""FastAPI application entry point and factory for SmogShield."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from api.middleware.cors import configure_cors
from api.middleware.rate_limiter import RateLimitMiddleware, SlidingWindowRateLimiter
from api.middleware.security import MaxBodySizeMiddleware, SecurityHeadersMiddleware
from api.routes import aqi, chat, health, recommendations, tools
from api.spa import mount_spa
from config import Settings, get_settings
from services.aqi_service import AQIService
from services.cache_service import TTLCache
from services.gemini_service import GeminiService
from services.recommendation_engine import RecommendationEngine
from services.weather_service import WeatherService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    static_dir: Path | None = None,
) -> FastAPI:
    """Create and configure a FastAPI instance with middleware, services, and routes."""
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        description=(
            "GenAI-powered Urban Air Quality Assistant providing real-time AQI analytics, "
            "personalized low-emission daily routines, indoor air hacks, and impact metrics."
        ),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    cache = TTLCache(
        ttl_seconds=app_settings.cache_ttl_seconds,
        max_entries=app_settings.cache_max_entries,
    )
    ai_cache = TTLCache(ttl_seconds=600, max_entries=100)
    weather_service = WeatherService(settings=app_settings, cache=cache)
    aqi_service = AQIService(
        settings=app_settings, cache=cache, weather_service=weather_service
    )
    recommendation_engine = RecommendationEngine()
    gemini_service = GeminiService(
        settings=app_settings,
        recommendation_engine=recommendation_engine,
        cache=ai_cache,
    )
    rate_limiter = SlidingWindowRateLimiter(window_seconds=60)

    app.state.settings = app_settings
    app.state.cache = cache
    app.state.ai_cache = ai_cache
    app.state.weather_service = weather_service
    app.state.aqi_service = aqi_service
    app.state.recommendation_engine = recommendation_engine
    app.state.gemini_service = gemini_service
    app.state.rate_limiter = rate_limiter

    configure_cors(app, app_settings)
    app.add_middleware(GZipMiddleware, minimum_size=500)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=16 * 1024)
    app.add_middleware(
        RateLimitMiddleware,
        chat_limit_per_min=app_settings.rate_limit_chat_per_min,
        aqi_limit_per_min=app_settings.rate_limit_aqi_per_min,
        limiter=rate_limiter,
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(aqi.router, prefix="/api")
    app.include_router(recommendations.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(tools.router, prefix="/api")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch unexpected exceptions without leaking stack traces to clients."""
        logger.exception("Unhandled error processing %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred. Please try again shortly."},
        )

    mount_spa(app, static_dir=static_dir)
    return app


app = create_app()
