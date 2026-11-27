"""Personalized recommendations and daily schedule endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request

from models.enums import BudgetLevel, CommuteType, HomeType
from models.schemas import RecommendationsResponse, UserProfile
from services.aqi_service import AQIService, CityNotFoundError, ExternalServiceError
from services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{city}", response_model=RecommendationsResponse)
async def get_recommendations_for_city(
    request: Request,
    city: str,
    family_members: int = Query(default=3, ge=1, le=20),
    has_children: bool = Query(default=False),
    has_elderly: bool = Query(default=False),
    health: list[str] = Query(default_factory=list),
    commute_type: CommuteType = Query(default=CommuteType.CAR),
    home_type: HomeType = Query(default=HomeType.APARTMENT),
    has_air_purifier: bool = Query(default=False),
    budget: BudgetLevel = Query(default=BudgetLevel.MEDIUM),
) -> RecommendationsResponse:
    """Return personalized routines, indoor hacks, and sustainable alternatives for a city."""
    aqi_service: AQIService = request.app.state.aqi_service
    engine: RecommendationEngine = request.app.state.recommendation_engine

    try:
        profile = UserProfile(
            city=city,
            family_members=family_members,
            has_children=has_children,
            has_elderly=has_elderly,
            health_conditions=health,
            commute_type=commute_type,
            home_type=home_type,
            has_air_purifier=has_air_purifier,
            budget=budget,
        )
        snapshot = await aqi_service.get_current_aqi(profile.city)
        return engine.generate(snapshot, profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("", response_model=RecommendationsResponse)
async def post_recommendations(
    request: Request, profile: UserProfile
) -> RecommendationsResponse:
    """Generate personalized recommendations from a complete household profile payload."""
    aqi_service: AQIService = request.app.state.aqi_service
    engine: RecommendationEngine = request.app.state.recommendation_engine

    try:
        snapshot = await aqi_service.get_current_aqi(profile.city)
        return engine.generate(snapshot, profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
