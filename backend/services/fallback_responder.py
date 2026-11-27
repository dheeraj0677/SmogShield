"""Deterministic context-grounded conversational fallback responder."""

from models.schemas import AQISnapshot, RecommendationItem, RecommendationsResponse


def build_fallback_reply(
    message: str,
    snapshot: AQISnapshot,
    rec_package: RecommendationsResponse,
    top_recs: list[RecommendationItem],
) -> str:
    """Generate a well-structured, context-grounded reply without external LLM keys."""
    pm25_text = (
        f"{snapshot.pollutants.pm25} µg/m³"
        if snapshot.pollutants.pm25 is not None
        else "elevated"
    )
    wind_text = (
        f"{snapshot.weather.wind_speed_kmh} km/h"
        if snapshot.weather.wind_speed_kmh is not None
        else "light"
    )
    intro = (
        f"**Current Air Quality Snapshot — {snapshot.resolved_city}:**\n"
        f"Right now the AQI is **{snapshot.aqi} ({snapshot.category_label})** with PM2.5 at "
        f"**{pm25_text}** and wind at **{wind_text}** ({snapshot.weather.smog_trapping_risk} "
        f"smog-trapping risk)."
    )
    if rec_package.effective_aqi > snapshot.aqi:
        intro += (
            f" Because your household includes sensitive considerations "
            f"({rec_package.personalization_summary.split('|')[1].strip()}), treat today's "
            f"effective risk as **AQI {rec_package.effective_aqi}**."
        )

    action_lines = [
        f"{idx}. **{rec.title}** ({rec.best_time}): {rec.description}\n"
        f"   *Direct impact:* {rec.impact} (`{rec.impact_metric}`)"
        for idx, rec in enumerate(top_recs, start=1)
    ]

    lowered = message.lower()
    contextual_note = ""
    if any(word in lowered for word in ("asthma", "breathe", "cough", "inhaler", "doctor")):
        contextual_note = (
            "\n\n**Health Note:** Keep prescribed inhalers close at hand and consult a "
            "physician promptly if anyone experiences wheezing or shortness of breath."
        )
    elif any(word in lowered for word in ("window", "ventilat", "air out")):
        contextual_note = f"\n\n**Ventilation Timing:** {snapshot.weather.dispersion_note} " + (
            "Keep windows sealed during morning and evening rush hours."
            if rec_package.effective_aqi > 100
            else "A brief 20-minute cross-breeze around 1:30 PM is safe today."
        )

    return (
        f"{intro}\n\n**Tailored Action Plan for Your Query:**\n"
        + "\n".join(action_lines)
        + contextual_note
    )
