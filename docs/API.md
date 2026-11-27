# SmogShield API Reference

Base URL (local): `http://localhost:8000/api`  
Interactive Swagger UI: `http://localhost:8000/api/docs`

## Endpoints

### 1. Health Check
- `GET /api/health`
- Returns service status, version, environment, and configured data/AI providers.

### 2. Live AQI Lookup by City
- `GET /api/aqi/{city}`
- Validates city string (`2-80` chars), checks TTL cache (15-min TTL), fetches live WAQI or Open-Meteo pollutant readings + weather/smog dispersion risk, and returns normalized `AQISnapshot`.
- Errors: `400` (invalid syntax), `404` (city not found), `429` (rate limit exceeded).

### 3. Live AQI Lookup by Coordinates
- `GET /api/aqi/coordinates?lat={lat}&lon={lon}`
- Resolves browser geolocation coordinates to live Open-Meteo pollutants and weather.

### 4. Personalized Recommendations
- `GET /api/recommendations/{city}` (query params for household profile)
- `POST /api/recommendations` (JSON `UserProfile` body)
- Returns `RecommendationsResponse` including `effective_aqi`, `daily_routine`, `indoor_hacks`, `alternatives`, `health_protections`, `schedule`, `total_potential_co2_saved_kg`, and `estimated_exposure_reduction_pct`.

### 5. GenAI Conversational Assistant
- `POST /api/chat`
- Body: `{ "message": "...", "city": "Delhi", "user_profile": {...}, "history": [...] }`
- Neutralizes XSS/prompt injection, injects real-time AQI & household context, invokes Gemini (with automatic deterministic fallback if unconfigured/offline), and returns `ChatResponse` with `reply`, `recommendations`, `impact_summary`, `follow_up_prompts`, and safety `disclaimer`.
