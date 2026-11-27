"""Engineering tools routes: Room CADR/ACH calculator, Dijkstra clean commute, cache stats."""

from fastapi import APIRouter, HTTPException, Request

from models.schemas import (
    CADRRequest,
    CADRResponse,
    CommuteModeOption,
    CommutePlanRequest,
    CommutePlanResponse,
)
from services.aqi_service import AQIService, CityNotFoundError, ExternalServiceError
from services.cache_service import TTLCache
from utils.cadr_calculator import compute_cadr_analysis
from utils.commute_dose import compute_commute_comparison
from utils.dijkstra_router import find_cleanest_corridor

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/cadr", response_model=CADRResponse)
async def calculate_room_cadr(payload: CADRRequest) -> CADRResponse:
    """Compute room Air Changes per Hour (ACH) and clean-air decay time."""
    result = compute_cadr_analysis(
        room_area_sqft=payload.room_area_sqft,
        ceiling_height_ft=payload.ceiling_height_ft,
        outdoor_pm25=payload.outdoor_pm25,
        purifier_cadr_m3h=payload.purifier_cadr_m3h,
        seal_quality=payload.seal_quality,
    )
    return CADRResponse(**result)


@router.post("/commute-plan", response_model=CommutePlanResponse)
async def calculate_commute_plan(
    request: Request, payload: CommutePlanRequest
) -> CommutePlanResponse:
    """Compute Dijkstra lowest-exposure corridor and modal PM2.5/CO2 comparisons."""
    aqi_service: AQIService = request.app.state.aqi_service
    try:
        snapshot = await aqi_service.get_current_aqi(payload.city)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    ambient_pm25 = snapshot.pollutants.pm25 if snapshot.pollutants.pm25 is not None else 45.0
    corridor = find_cleanest_corridor(
        ambient_aqi=snapshot.aqi,
        ambient_pm25=ambient_pm25,
        distance_km=payload.distance_km,
    )
    modes = compute_commute_comparison(
        distance_km=payload.distance_km,
        ambient_pm25=ambient_pm25,
        wear_n95_mask=payload.wear_n95_mask,
    )
    return CommutePlanResponse(
        city=snapshot.resolved_city,
        ambient_aqi=snapshot.aqi,
        ambient_pm25=ambient_pm25,
        corridor_analysis=corridor,
        mode_comparisons=[CommuteModeOption(**item) for item in modes],
    )


@router.get("/cache-stats")
async def get_cache_stats(request: Request) -> dict:
    """Return live LRU+TTL cache hit/miss telemetry for efficiency monitoring."""
    data_cache: TTLCache = request.app.state.cache
    ai_cache: TTLCache = request.app.state.ai_cache
    return {
        "aqi_weather_cache": data_cache.stats(),
        "ai_response_cache": ai_cache.stats(),
    }
