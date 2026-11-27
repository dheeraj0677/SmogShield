"""Conversational GenAI chat endpoint."""

from fastapi import APIRouter, HTTPException, Request

from models.schemas import ChatRequest, ChatResponse, UserProfile
from services.aqi_service import AQIService, CityNotFoundError, ExternalServiceError
from services.gemini_service import GeminiService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_assistant(request: Request, payload: ChatRequest) -> ChatResponse:
    """Process a user query with real-time AQI context and household profile."""
    aqi_service: AQIService = request.app.state.aqi_service
    gemini_service: GeminiService = request.app.state.gemini_service

    profile = payload.user_profile or UserProfile(city=payload.city)
    target_city = payload.city or profile.city

    try:
        snapshot = await aqi_service.get_current_aqi(target_city)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return await gemini_service.generate_chat_response(
        message=payload.message,
        aqi_snapshot=snapshot,
        user_profile=profile,
        history=payload.history,
    )
