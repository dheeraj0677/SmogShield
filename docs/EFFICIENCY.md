# Efficiency & Resource Optimization — SmogShield

## Measured Production Footprint

- **Frontend Production Bundle (`vite build`)**:
  - JavaScript: `241.64 kB` raw / **`70.45 kB` gzipped**
  - CSS: `47.28 kB` raw / **`7.76 kB` gzipped**
  - Zero third-party charting libraries (Recharts/Chart.js omitted in favor of native lightweight SVG components in `SmogSparkline.jsx` and `AQIGauge.jsx`).
- **Git Repository Size**: `2.63 MB` tracked (strictly `< 10 MB` limit).

## Caching & API Reduction Architecture

1. **Single-Round-Trip Telemetry Batching (`aqi_service.py`)**:
   - Fetches current pollutants (`us_aqi`, `pm2_5`, `pm10`, `co`, `no2`, `so2`, `o3`) AND 24-hour diurnal trend (`hourly=pm2_5,us_aqi`) in **one** Open-Meteo HTTP call.
2. **Bounded LRU + TTL Cache (`cache_service.py`)**:
   - **AQI & Weather Cache**: 15-minute TTL (`256` max entries), preventing redundant upstream calls while serving repeat city lookups from memory.
   - **SHA-256 AI Response Cache**: 10-minute TTL (`100` max entries) keyed on SHA-256 hash of `(city, aqi_bucket, query, household_profile)` — cuts repeated LLM latency and API quota consumption.
3. **Response Compression (`main.py`)**:
   - `GZipMiddleware(minimum_size=500)` compresses JSON payloads cleanly over HTTP.
4. **React Render Efficiency**:
   - `SmogSparkline` memoized with `React.memo`; household context persisted locally (`localStorage`) without redundant backend profile round-trips.
