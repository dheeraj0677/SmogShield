# SmogShield — Urban Air Quality & Winter Smog Assistant

[![CI Pipeline](https://github.com/dheeraj0677/SmogShield/actions/workflows/ci.yml/badge.svg)](https://github.com/dheeraj0677/SmogShield/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab.svg)](backend/requirements.txt)
[![React 18 + Vite](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-0ea5e9.svg)](frontend/package.json)
[![Tests: 84 Passing](https://img.shields.io/badge/Tests-84%20%2F%2084%20Passing-15803d.svg)](docs/TESTING.md)

**SmogShield** is a GenAI-powered public-health and urban air quality advisor built for **PromptWars Challenge 6: Urban Air Quality Assistant**. It helps families, sensitive households, and commuters navigate severe winter smog episodes with live multi-pollutant telemetry, context-aware daily routines, room-level air filtration sizing, lowest-exposure commute routing, and quantified CO₂ and PM2.5 impact tracking.

---

## Table of Contents

1. [Chosen Challenge Vertical](#1-chosen-challenge-vertical)
2. [Approach & Decision Logic](#2-approach--decision-logic)
3. [System Architecture & How It Works](#3-system-architecture--how-it-works)
4. [Key Capabilities](#4-key-capabilities)
5. [Quick Start](#5-quick-start)
6. [Configuration & Environment Variables](#6-configuration--environment-variables)
7. [Evaluation Evidence & Verification](#7-evaluation-evidence--verification)
8. [Assumptions & Limitations](#8-assumptions--limitations)
9. [Project Structure](#9-project-structure)
10. [License](#10-license)

---

## 1. Chosen Challenge Vertical

**Vertical:** `[Challenge 6] Urban Air Quality Assistant`

### The Problem Addressed

During winter temperature inversions, cold stagnant air traps vehicular exhaust, residential combustion, and particulate matter (`PM2.5`, `PM10`, `NO₂`) close to ground level across urban centers (such as Delhi, Lahore, Lucknow, Dhaka, and Beijing). Standard AQI widgets show only raw index numbers and fail to answer practical household questions:

- _When is it safe for children or older adults to step outside or ventilate rooms?_
- _Can a family without an expensive purifier clean a bedroom on a low budget?_
- _Which commute mode or corridor minimizes actual inhaled particulate dose, and what is the direct carbon/health impact of switching?_

### Target Personas

- **Vulnerable Families:** Households with children, older adults, or members managing asthma, COPD, allergies, or heart conditions.
- **Urban Commuters:** Daily travelers weighing metro, car, motorbike, walking, cycling, and remote work options.
- **Neighborhood Communities:** Local residents adopting zero-burn practices and sharing multilingual emergency advisories.

---

## 2. Approach & Decision Logic

SmogShield uses a **hybrid deterministic + Generative AI architecture** so environmental advice is mathematically grounded, personalized to household context, and never fabricated by an LLM:

1. **Multi-Tier Live Telemetry (`aqi_service.py`, `weather_service.py`)**:
   - Queries **WAQI** and **OpenWeatherMap** when API tokens are supplied, or automatically uses keyless **Open-Meteo** APIs out of the box—fetching current `PM2.5`, `PM10`, `O₃`, `NO₂`, `SO₂`, `CO`, meteorology, and a **24-hour diurnal AQI curve** in a single upstream call.
   - Evaluates **winter smog-trapping risk** (`low` / `moderate` / `high`) from wind speed (`<7 km/h`), ambient temperature, and relative humidity.
   - Falls back to curated baseline city profiles (`constants.py`) if external networks are unreachable.
2. **US EPA AQI & Household Sensitivity Adjustment (`aqi_calculator.py`)**:
   - Computes sub-indices across all six criteria pollutants using **2024 US EPA PM2.5 breakpoints** (`0–500` scale).
   - Shifts the effective risk posture upward (`+20` to `+60` AQI points) when children, elderly adults, or respiratory/cardiovascular conditions are present.
3. **Pure Environmental Engineering Solvers (`backend/utils/`)**:
   - **Room CADR & Decay Solver (`cadr_calculator.py`)**: Calculates room volume, Air Changes per Hour (`ACH`), recommended CADR for the `4.8 ACH` clean-room benchmark, and minutes required to bring indoor `PM2.5` below `15 µg/m³` for either commercial HEPA units or low-cost **Corsi-Rosenthal DIY box-fan filters**.
   - **Dijkstra Clean-Corridor Router (`dijkstra_router.py`)**: Evaluates urban corridor segments weighted by cumulative inhaled `PM2.5` dose (`µg`) rather than distance alone, comparing green/metro corridors against congested arterial roads.
   - **Commute Dose & CO₂ Engine (`commute_dose.py`)**: Quantifies round-trip inhaled `PM2.5` (`µg`) and tailpipe `CO₂` (`kg`) across six travel modes using respiratory minute-ventilation rates and N95 filtration factors.
4. **Context-Grounded GenAI Advisor (`gemini_service.py`)**:
   - Injects live AQI, dispersion risk, household profile, and top rule-backed interventions into strictly delimited `<environment_context>` and `<user_query>` prompts for **Google Gemini 2.0 Flash** (`google-genai`).
   - Uses a **SHA-256 response cache** (`10-min TTL`) and gracefully falls back to a structured, context-grounded advisor whenever `GEMINI_API_KEY` is omitted or an upstream call fails.

---

## 3. System Architecture & How It Works

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                     CLIENT — React 18 + Vite + Tailwind CSS                  │
│                     Production Bundle: 70.45 kB JS / 7.76 kB CSS (gzip)      │
│                                                                              │
│  • Header & Household Context Sidebar (City/GPS, Light/Dark Mode, Aa+)       │
│  • Live AQI Dashboard (EPA Meter, Pollutant Grid, Inversion Risk, SVG Trend) │
│  • Action Plans: Daily Routine │ Indoor Hacks + CADR │ Dijkstra Commute │    │
│                  Sustainable Alternatives │ Community Pledges & RTL Alerts   │
│  • Conversational GenAI Assistant (Grounded Replies + Quantified Impact)     │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │ HTTPS / REST + GZip
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND — Python 3.11+ / FastAPI                      │
│                                                                              │
│  Security Pipeline: CORS Allowlist → GZip → CSP/COOP/Security Headers        │
│                     → 16 KB Payload Limit (413) → JSON Check (415)           │
│                     → Sliding-Window Rate Limiter (30/min chat, 60/min AQI)  │
│                                                                              │
│  Services & Cache:  TTLCache (15m Data LRU + 10m SHA-256 AI LRU)             │
│                     RecommendationEngine + CADR + Dijkstra + CommuteDose     │
│                     GeminiService (Prompt Isolation + Leak Guard + Fallback) │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Request Lifecycle

1. **Context Selection:** The user selects a city (or uses browser GPS) and configures family size, sensitive groups, health conditions, commute mode, home type, and budget in the sidebar (persisted in `localStorage`).
2. **Telemetry & Planning (`POST /api/recommendations`):** The backend resolves cached or live AQI + meteorology, computes sensitivity-adjusted alerts, builds a 4-window daily schedule, and quantifies cumulative `kg CO₂` saved and `% PM2.5` exposure reduction.
3. **Interactive Solvers (`POST /api/tools/cadr`, `POST /api/tools/commute-plan`):** Users test bedroom CADR/ACH configurations or run Dijkstra lowest-exposure commute comparisons tailored to live city pollution.
4. **Grounded Conversation (`POST /api/chat`):** Queries are sanitized, checked against prompt-injection heuristics, matched against the SHA-256 AI cache, and answered by Gemini (or deterministic fallback) with attached direct-impact recommendation cards.

---

## 4. Key Capabilities

- **Real-Time AQI & 24h Diurnal Cycle:** Circular US EPA gauge (`role="meter"`), 6-pollutant breakdown, thermal inversion risk indicator, and native SVG 24-hour trend chart with paired `.sr-only` text summaries.
- **Tailored Daily Routines & Indoor Hacks:** Shifts workouts indoors during morning/evening inversions, schedules midday ventilation windows when safe, and matches filtration strategies (`DIY box-fan` vs `True HEPA`) to household budget.
- **Clean-Corridor Commute Planner:** Dijkstra pathfinding and 6-mode table quantifying both inhaled `PM2.5` (`µg`) and `CO₂` (`kg`) with optional N95 toggling.
- **Direct Impact Explainer:** Every suggestion states explicit health exposure reductions and daily carbon savings (`ImpactMeter.jsx`, `MessageBubble.jsx`).
- **Multilingual Community Hub:** Interactive neighborhood clean-air pledges plus emergency advisories in **English**, **Hindi (`हिन्दी`)**, **Urdu (`اردو` with automatic RTL `dir="rtl"`)**, and **Spanish (`Español`)**.
- **Inclusive Accessibility:** Clean Light & Dark themes, **`Aa+` Large Text** toggle, keyboard skip links, dual text+color indicators, and `prefers-reduced-motion` support.

---

## 5. Quick Start

### Prerequisites

- **Python** `3.11+`
- **Node.js** `20+` and `npm`

### Option A: Local Development

**1. Start the Backend API**

```bash
cd backend
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # Optional: add API keys (works zero-config via Open-Meteo)
uvicorn main:app --reload --port 8000
```

Interactive OpenAPI / Swagger docs are served at `http://localhost:8000/api/docs`.

**2. Start the Frontend UI**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Option B: Deploy on Render (1-Click Blueprint)

SmogShield includes a unified multi-stage [`Dockerfile`](Dockerfile) and [`render.yaml`](render.yaml) Blueprint serving both the FastAPI backend (`/api/*`) and built React UI (`/`) from a single origin on Render's Free Tier:

1. In the **Render Dashboard**, click **New + -> Blueprint** and connect `https://github.com/dheeraj0677/SmogShield`.
2. When prompted, enter your `OPENROUTER_API_KEY` (and optionally `GEMINI_API_KEY` / `GOOGLE_AIR_QUALITY_API_KEY`).
3. Render automatically builds `frontend/dist` + FastAPI, sets `$PORT` and `RENDER_EXTERNAL_URL`, and monitors `/api/health`.

### Option C: Docker Compose

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/health`

---

## 6. Configuration & Environment Variables

All external keys are optional—SmogShield runs out of the box using keyless Open-Meteo telemetry and its built-in rule-based response synthesizer. Copy [`backend/.env.example`](backend/.env.example) to `backend/.env` to customize:

| Variable                  | Purpose                                  | Default / Behavior                                               |
| ------------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| `OPENROUTER_API_KEY`      | OpenRouter API key (`:free` models only) | Optional; preferred LLM when set                                 |
| `OPENROUTER_MODEL`           | OpenRouter free model ID                 | `google/gemma-4-26b-a4b-it:free` (enforces `:free` models only)   |
| `GEMINI_API_KEY`             | Google Gemini API key                    | Optional; used if OpenRouter is unset; falls back to rule engine  |
| `GEMINI_MODEL`               | Gemini model ID                          | `gemini-2.0-flash`                                                |
| `GOOGLE_AIR_QUALITY_API_KEY` | Google Air Quality API v1 key            | Optional; used before Open-Meteo when set                         |
| `WAQI_API_TOKEN`             | World Air Quality Index token            | Optional; falls back to Google AQI / keyless Open-Meteo if unset  |
| `OPENWEATHER_API_KEY`     | OpenWeatherMap key                       | Optional; falls back to live keyless Open-Meteo if unset         |
| `CORS_ORIGINS`            | Allowed frontend origins                 | `http://localhost:5173,http://127.0.0.1:5173`                    |
| `CACHE_TTL_SECONDS`       | AQI & weather cache TTL                  | `900` (15 minutes)                                               |
| `RATE_LIMIT_CHAT_PER_MIN` | Per-IP `/api/chat` limit                 | `30`                                                             |
| `RATE_LIMIT_AQI_PER_MIN`  | Per-IP AQI/tool route limit              | `60`                                                             |

---

## 7. Evaluation Evidence & Verification

Detailed reports for every evaluation focus area live in [`docs/`](docs/):

| Focus Area            | Summary                     | Verified Evidence                                                                                  | Documentation                                          |
| --------------------- | --------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **Problem Alignment** | Full Challenge 6 coverage   | 8-requirement traceability matrix (`REQ-01`–`REQ-08`)                                              | [docs/PROBLEM_ALIGNMENT.md](docs/PROBLEM_ALIGNMENT.md) |
| **Code Quality**      | **0 lint errors**           | `ruff check .` (`0` errors), `eslint .` (`0` errors), `<=200`-line modular files                   | [docs/CODE_QUALITY.md](docs/CODE_QUALITY.md)           |
| **Security**          | OWASP Top 10 & CWE hardened | `16 KB` cap (`413`), `415` JSON guard, rate limiter (`429`), CSP/COOP, SHA-256 cache, `0` prod npm vulns | [docs/SECURITY.md](docs/SECURITY.md)                   |
| **Efficiency**        | Lean footprint & caching    | `70.45 kB` JS / `7.76 kB` CSS gzipped, GZip middleware, single-call hourly+current telemetry       | [docs/EFFICIENCY.md](docs/EFFICIENCY.md)               |
| **Testing**           | **86 / 86 tests passing**   | `65` Pytest (`92%` cov) + `19` Vitest (`90.76%` cov) + `2` Playwright + Axe Chrome E2E             | [docs/TESTING.md](docs/TESTING.md)                     |
| **Accessibility**     | **0 axe violations**        | Verified WCAG 2.1 AA via `@axe-core/playwright`, Light/Dark mode, `Aa+`, `.sr-only` twins, RTL Urdu | [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md)         |
| **Google Services**   | Multi-service               | Google Gemini (`google-genai`), Google Air Quality API v1, Google Fonts, Gemma 4 (`:free`), Chrome | [docs/GOOGLE_SERVICES.md](docs/GOOGLE_SERVICES.md)     |

### Running Verification Commands

```bash
# Backend lint + tests + coverage
cd backend
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pytest --cov=. --cov-report=term-missing

# Frontend lint + unit tests + production build
cd ../frontend
npm run lint
npm test
npm run build

# End-to-end Chrome smoke test (with backend on :8000 and frontend on :5173)
npm run test:e2e
```

---

## 8. Assumptions & Limitations

1. **AQI Scale:** All index calculations follow the **US EPA AQI standard (0–500)** incorporating the 2024 US EPA PM2.5 breakpoint thresholds.
2. **Advisory Scope:** SmogShield provides environmental and lifestyle guidance only and does not offer medical diagnoses or clinical treatment advice.
3. **Network & Free-Tier Resilience:** Live lookups use keyless Open-Meteo (or WAQI/OpenWeatherMap when keys are provided); if offline, known urban centers gracefully fall back to curated baseline profiles.
4. **Impact Modeling:** Commute `PM2.5` doses (`µg`), `CO₂` savings (`kg`), and room CADR decay estimates use standard urban adult minute-ventilation and indoor infiltration parameters to communicate comparative behavioral impacts clearly.

---

## 9. Project Structure

```text
SmogShield/
├── .github/workflows/ci.yml        # Automated CI (Ruff, Pytest, ESLint, Vitest, Vite Build)
├── docs/                           # API, Architecture, & Evaluation Pillar Reports
│   ├── ACCESSIBILITY.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CODE_QUALITY.md
│   ├── EFFICIENCY.md
│   ├── PROBLEM_ALIGNMENT.md
│   ├── SECURITY.md
│   └── TESTING.md
├── backend/                        # FastAPI API, Compute Solvers, Services & Pytest Suite
│   ├── api/ (middleware, routes)
│   ├── models/ (enums, schemas)
│   ├── services/ (aqi, weather, recommendation, gemini, cache)
│   ├── utils/ (aqi_calculator, cadr_calculator, commute_dose, dijkstra_router, validators)
│   ├── tests/
│   ├── Dockerfile
│   └── main.py
├── frontend/                       # React 18 + Vite + Tailwind CSS UI, Vitest & Playwright E2E
│   ├── e2e/smoke.spec.js
│   ├── public/
│   ├── src/ (components, hooks, services, utils, __tests__)
│   └── Dockerfile
├── docker-compose.yml
├── metadata.json
├── LICENSE
└── README.md
```

---

## 10. License

Distributed under the [MIT License](LICENSE).
