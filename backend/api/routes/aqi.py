"""Air Quality Index endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request

from models.schemas import AQISnapshot
from services.aqi_service import AQIService, CityNotFoundError, ExternalServiceError

router = APIRouter(prefix="/aqi", tags=["aqi"])


@router.get("/coordinates", response_model=AQISnapshot)
async def get_aqi_by_coordinates(
    request: Request,
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude"),
    label: str = Query(default="Your Location", min_length=2, max_length=60),
) -> AQISnapshot:
    """Return live AQI snapshot for geographic coordinates."""
    aqi_service: AQIService = request.app.state.aqi_service
    try:
        return await aqi_service.get_aqi_by_coordinates(lat, lon, label=label)
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{city}", response_model=AQISnapshot)
async def get_aqi_by_city(request: Request, city: str) -> AQISnapshot:
    """Return live AQI, pollutant breakdown, and smog meteorology for a city."""
    aqi_service: AQIService = request.app.state.aqi_service
    try:
        return await aqi_service.get_current_aqi(city)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
