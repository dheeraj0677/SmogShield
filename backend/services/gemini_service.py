"""LLM conversational service supporting OpenRouter free models, Gemini, and rule fallback."""

import logging

import httpx

from config import Settings, get_settings
from models.schemas import (
    AQISnapshot,
    ChatHistoryMessage,
    ChatResponse,
    RecommendationItem,
    RecommendationsResponse,
    UserProfile,
)
from services.cache_service import TTLCache
from services.fallback_responder import build_fallback_reply
from services.llm_providers import (
    call_gemini_api,
    call_openrouter_api,
    resolve_free_openrouter_model,
)
from services.prompt_builder import KEYWORD_BOOSTS, build_enriched_prompt
from services.recommendation_engine import RecommendationEngine
from utils.validators import detect_prompt_injection, neutralize_prompt_injection

logger = logging.getLogger(__name__)

__all__ = ["GeminiService", "resolve_free_openrouter_model"]


class GeminiService:
    """Orchestrates GenAI responses enriched with live AQI, weather, and household profile."""

    def __init__(
        self,
        settings: Settings | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        cache: TTLCache | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._engine = recommendation_engine or RecommendationEngine()
        self._ai_cache = cache or TTLCache(ttl_seconds=600, max_entries=100)

    async def generate_chat_response(
        self,
        message: str,
        aqi_snapshot: AQISnapshot,
        user_profile: UserProfile | None = None,
        history: list[ChatHistoryMessage] | None = None,
    ) -> ChatResponse:
        """Generate a context-aware AI response plus structured recommendation cards."""
        profile = user_profile or UserProfile(city=aqi_snapshot.resolved_city)
        rec_package = self._engine.generate(aqi_snapshot, profile)
        top_recs = self._select_relevant_recommendations(message, rec_package)

        safe_message = neutralize_prompt_injection(message)
        if detect_prompt_injection(message):
            logger.warning("Prompt injection pattern neutralized in user message.")

        cache_key = TTLCache.hash_key(
            "chat",
            {
                "city": aqi_snapshot.resolved_city.lower(),
                "aqi_bucket": aqi_snapshot.aqi // 15,
                "effective_aqi": rec_package.effective_aqi,
                "query": safe_message.lower(),
                "commute": profile.commute_type.value,
                "kids": profile.has_children,
                "elderly": profile.has_elderly,
                "conditions": sorted(profile.health_conditions),
                "budget": profile.budget.value,
            },
        )
        if not history:
            cached_reply = self._ai_cache.get(cache_key)
            if cached_reply is not None:
                return cached_reply.model_copy(update={"aqi_snapshot": aqi_snapshot})

        ai_provider = "smogshield-rule-engine"
        reply_text: str | None = None

        if self._settings.has_openrouter:
            or_reply, used_model = await self._call_openrouter(
                safe_message, aqi_snapshot, profile, rec_package, top_recs, history or []
            )
            if or_reply and not self._contains_prompt_leak(or_reply):
                reply_text = or_reply
                ai_provider = f"openrouter ({used_model})"

        if reply_text is None and self._settings.has_gemini:
            gemini_reply = await self._call_gemini(
                safe_message, aqi_snapshot, profile, rec_package, top_recs, history or []
            )
            if gemini_reply and not self._contains_prompt_leak(gemini_reply):
                reply_text = gemini_reply
                ai_provider = f"gemini ({self._settings.gemini_model})"

        if reply_text is None:
            reply_text = build_fallback_reply(safe_message, aqi_snapshot, rec_package, top_recs)

        response = ChatResponse(
            reply=reply_text,
            recommendations=top_recs,
            aqi_snapshot=aqi_snapshot,
            impact_summary=(
                f"Acting on these suggestions can cut your household's PM2.5 exposure by up to "
                f"{rec_package.estimated_exposure_reduction_pct}% and save roughly "
                f"{rec_package.total_potential_co2_saved_kg:.1f} kg CO2 today."
            ),
            ai_provider=ai_provider,
            follow_up_prompts=self._build_follow_up_prompts(aqi_snapshot, profile),
        )
        if not history:
            self._ai_cache.set(cache_key, response, ttl_seconds=600)
        return response

    @staticmethod
    def _contains_prompt_leak(text: str) -> bool:
        """Prevent accidental leakage of internal prompt boundary delimiters."""
        markers = ("<environment_context>", "<household_profile>", "STRICT SAFETY & GROUNDING")
        return any(marker in text for marker in markers)

    async def _call_openrouter(
        self,
        safe_message: str,
        aqi_snapshot: AQISnapshot,
        profile: UserProfile,
        rec_package: RecommendationsResponse,
        top_recs: list[RecommendationItem],
        history: list[ChatHistoryMessage],
        client: httpx.AsyncClient | None = None,
    ) -> tuple[str | None, str]:
        """Delegate OpenRouter invocation cleanly to provider helper."""
        enriched = build_enriched_prompt(
            safe_message, aqi_snapshot, profile, rec_package, top_recs, history
        )
        return await call_openrouter_api(self._settings, enriched, client=client)

    async def _call_gemini(
        self,
        safe_message: str,
        aqi_snapshot: AQISnapshot,
        profile: UserProfile,
        rec_package: RecommendationsResponse,
        top_recs: list[RecommendationItem],
        history: list[ChatHistoryMessage],
    ) -> str | None:
        """Delegate Gemini invocation cleanly to provider helper."""
        enriched = build_enriched_prompt(
            safe_message, aqi_snapshot, profile, rec_package, top_recs, history
        )
        return await call_gemini_api(self._settings, enriched)

    @staticmethod
    def _select_relevant_recommendations(
        message: str, rec_package: RecommendationsResponse
    ) -> list[RecommendationItem]:
        """Prioritize recommendation cards matching the user's question intent."""
        lowered = message.lower()
        pool = (
            rec_package.health_protections
            + rec_package.daily_routine
            + rec_package.indoor_hacks
            + rec_package.alternatives
        )
        boosted_tags: set[str] = set()
        for kw, tags in KEYWORD_BOOSTS.items():
            if kw in lowered:
                boosted_tags |= tags

        ranked = sorted(
            pool,
            key=lambda item: (len(set(item.tags) & boosted_tags), 6 - item.priority),
            reverse=True,
        )
        selected: list[RecommendationItem] = []
        for item in ranked:
            if item not in selected:
                selected.append(item)
            if len(selected) >= 4:
                break
        return selected

    @staticmethod
    def _build_follow_up_prompts(snapshot: AQISnapshot, profile: UserProfile) -> list[str]:
        """Suggest useful next questions tailored to current city and household."""
        first = (
            f"How should I plan school commute and indoor play in {snapshot.resolved_city} today?"
            if (profile.has_children or profile.has_elderly)
            else f"What is the safest time today in {snapshot.resolved_city} to open windows?"
        )
        return [
            first,
            "How can I make a low-cost DIY air purifier at home?",
            "How much emissions and exposure do I save by switching my commute?",
        ]
