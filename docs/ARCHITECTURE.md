# SmogShield Architecture

## System Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                       FRONTEND (React 18 + Vite)                     │
│  • AQIDashboard (Gauge, Pollutants, WeatherCard, SVG SmogSparkline)  │
│  • Recommendation Tabs (DailyRoutine, IndoorHacks+CADR,              │
│    TransitPlanner Dijkstra Router, AlternativesList, CommunityHub)   │
│  • ChatWindow (Grounded GenAI Assistant + Direct Impact Cards)       │
│  • Accessibility (Light / Dark Mode, Aa+ Text, .sr-only SVG twins)    │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ REST /api (GZip + CORS)
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI + Python)                     │
│  Security Pipeline: CORS → GZip → SecurityHeaders → MaxBodySize(16K) │
│                     → SlidingWindowRateLimiter (30/min chat, 60 AQI) │
│                                                                      │
│  Services: AQIService (WAQI / Open-Meteo + 24h Trend + 15m TTLCache) │
│            WeatherService (OWM / Open-Meteo + Thermal Inversion)     │
│            RecommendationEngine + CADR + Dijkstra + CommuteDose      │
│            GeminiService (SHA-256 AI Cache + Prompt Guard + Fallback)│
└──────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Hybrid Rules + GenAI Grounding**: Pure Python modules compute US EPA 2024 AQI indices, room ACH decay timelines (`cadr_calculator.py`), Dijkstra lowest-exposure corridors (`dijkstra_router.py`), and respiratory minute-ventilation PM2.5 doses (`commute_dose.py`). `GeminiService` injects these verified metrics into delimited prompts and degrades cleanly to rule-based synthesis if `GEMINI_API_KEY` is omitted or fails.
2. **Zero-Config Live Telemetry**: Works immediately out-of-the-box via keyless **Open-Meteo** (current pollutants + 24h hourly trend in one request + meteorology), while supporting **WAQI** and **OpenWeatherMap** tokens when configured.
3. **Lightweight Native Visualizations**: Custom inline SVG sparklines and circular meters keep the gzipped JavaScript bundle at **`66.15 kB`** with paired `.sr-only` text twins for screen readers.
