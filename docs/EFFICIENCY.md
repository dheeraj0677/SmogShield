# Efficiency & Resource Optimization — SmogShield

## Measured Production Footprint

- **Frontend Production Bundle (`vite build`)**:
  - JavaScript: `223.68 kB` raw / **`66.15 kB` gzipped**
  - CSS: `33.08 kB` raw / **`6.17 kB` gzipped**
  - Zero third-party charting libraries (Recharts/Chart.js omitted in favor of native lightweight SVG components in `SmogSparkline.jsx` and `AQIGauge.jsx`).
- **Git Repository Size**: `< 0.6 MB` tracked (strictly `< 10 MB` rule).

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
