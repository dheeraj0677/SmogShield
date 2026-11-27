# SmogShield API Reference

Base URL (local): `http://localhost:8000/api`  
Interactive Swagger UI: `http://localhost:8000/api/docs`

## Endpoints

### 1. Health Check
- `GET /api/health`
- Returns service liveness, version, environment, and configured data/AI providers.

### 2. Live AQI & 24h Diurnal Trend
- `GET /api/aqi/{city}` — Validates city name (`2-80` chars), checks TTL cache (15-min TTL), fetches live WAQI or Open-Meteo current pollutants + 24h hourly trend + smog-trapping meteorology.
- `GET /api/aqi/coordinates?lat={lat}&lon={lon}` — Resolves browser GPS coordinates to live pollutants and hourly trend.

### 3. Personalized Recommendations
- `GET /api/recommendations/{city}` (query params for household profile)
- `POST /api/recommendations` (JSON `UserProfile` body)
- Returns `effective_aqi`, `daily_routine`, `indoor_hacks`, `alternatives`, `health_protections`, `schedule`, `total_potential_co2_saved_kg`, and `estimated_exposure_reduction_pct`.

### 4. GenAI Conversational Assistant
- `POST /api/chat`
- Enforces `16 KB` max JSON body (`413`), JSON Content-Type (`415`), sliding-window rate limit (`429`), prompt-injection neutralization, SHA-256 AI response caching, and prompt-leak guards.

### 5. Engineering Tools & Cache Telemetry
- `POST /api/tools/cadr` — Room CADR / ACH solver (`minutes_to_safe_air`, `recommended_cadr_m3h`, `meets_target_ach`).
- `POST /api/tools/commute-plan` — Runs Dijkstra clean-corridor pathfinder and returns 6-mode PM2.5 inhaled dose & CO₂ comparison.
- `GET /api/tools/cache-stats` — Returns hit/miss counts and hit-rate percentages for both caches.
