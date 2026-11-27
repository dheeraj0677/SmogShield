# SmogShield Architecture

## Overview

SmogShield is split into two cleanly decoupled layers:

1. **Frontend (`frontend/`)** — React 18 + Vite + Tailwind CSS SPA designed around WCAG 2.1 AA accessibility, responsive mobile/desktop layout, and persistent household context (`localStorage`).
2. **Backend (`backend/`)** — Async FastAPI REST service structured into routes, middleware, services, Pydantic models, and domain utilities.

## Key Design Decisions

- **Hybrid Intelligence (Deterministic Rules + GenAI)**:
  - A rule-based `RecommendationEngine` computes exact US EPA sub-indices, adjusts risk thresholds for vulnerable groups (children, elderly, asthma/COPD), and builds quantified impact metrics (`kg CO2 saved`, `% PM2.5 exposure reduction`).
  - `GeminiService` injects live AQI, smog-trapping meteorology (wind speed, temperature, humidity), household context, and evidence-backed recommendations into a delimited prompt so the LLM stays grounded and never fabricates air readings.
  - If no `GEMINI_API_KEY` is provided or an upstream call fails, the engine seamlessly falls back to structured context-grounded generation.

- **Zero-Config Live Air Quality + Resilience**:
  - Supports **WAQI** and **OpenWeatherMap** when keys are configured in `.env`.
  - Automatically uses keyless **Open-Meteo** Geocoding, Air Quality, and Forecast APIs out of the box so evaluators receive live readings with zero setup.
  - Falls back to curated urban baselines when upstream networks are unreachable.

- **Defense-in-Depth Security**:
  - Pydantic schema validation + HTML/script sanitization + city path-traversal rejection.
  - Delimited prompt isolation + prompt-injection pattern neutralization.
  - Sliding-window per-IP rate limiting (`30 req/min` chat, `60 req/min` AQI) with `Retry-After`.
  - Strict CORS allowlist and security headers (`CSP`, `X-Frame-Options`, `X-Content-Type-Options`).
