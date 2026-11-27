# 🛡️ SmogShield — Urban Air Quality Assistant

> A GenAI-powered assistant that helps families and communities navigate severe winter smog and urban air pollution by suggesting low-emission daily routines, practical indoor air quality hacks, and sustainable alternatives tailored to location and household context—with clear explanations of the direct impact of every choice.

---

## 🎯 Chosen Challenge Vertical

**Challenge 6: Urban Air Quality Assistant (PromptWars Virtual)**

SmogShield focuses on households living in winter-smog and high-pollution urban corridors (such as Delhi, Lahore, Lucknow, Dhaka, and Beijing) as well as global cities experiencing acute air-quality events.

---

## 💡 Approach & Logic

SmogShield combines **live environmental telemetry**, **deterministic environmental health rules**, and **Generative AI** in a hybrid architecture:

1. **Real-Time AQI & Smog Meteorology**:
   - Fetches live particulate (`PM2.5`, `PM10`) and gas (`O3`, `NO2`, `SO2`, `CO`) readings plus weather (`temperature`, `humidity`, `wind speed`).
   - Computes US EPA AQI sub-indices (including the updated 2024 US EPA PM2.5 breakpoints) and evaluates **winter smog-trapping / thermal inversion risk** (e.g., stagnant winds `<7 km/h` + cool/humid air trap soot near breathing height).
2. **Household Sensitivity Adjustment**:
   - Adjusts the effective AQI risk upward (`+20` to `+60` points) when the household includes children, elderly adults, or respiratory/cardiovascular conditions such as asthma or COPD.
3. **Hybrid Recommendation Engine (`backend/services/recommendation_engine.py`)**:
   - **Daily Routine & Time-Window Schedule**: Recommends when to exercise, commute, seal windows during rush hour, and safely cross-ventilate.
   - **Indoor Air Quality Hacks**: Adapts to budget and home setup—suggesting low-cost **Corsi-Rosenthal DIY box-fan + MERV-13/HEPA filters** for tight budgets, True HEPA clean-air sleep sanctuaries, wet microfiber mopping (avoiding dust resuspension), kitchen exhaust hygiene, and draft sealing.
   - **Sustainable Alternatives with Quantified Direct Impact**: Recommends metro/carpool commutes, work-from-home smog days, zero-burn neighborhood heating/waste habits, and consolidated deliveries, showing both **CO₂ saved (kg/day)** and **PM2.5 exposure reduction (%)**.
4. **Grounded GenAI Conversational Assistant (`backend/services/gemini_service.py`)**:
   - Injects live AQI, weather dispersion notes, household profile, and top rule-backed interventions into a strictly delimited prompt for **Google Gemini**.
   - Automatically degrades gracefully to an intelligent context-grounded rule-based advisor if `GEMINI_API_KEY` is omitted or an external LLM call fails.

---

## ⚙️ How the Solution Works

```text
User (Browser: React + Vite + Tailwind)
   │
   ├──► Selects City / GPS + Household Profile (kids, asthma, commute, budget)
   │
   ├──► GET/POST /api/recommendations ──► AQIService (WAQI or Open-Meteo + 15m TTLCache)
   │                                         └─► RecommendationEngine ─► Routines, Hacks, Alternatives + Impact
   │
   └──► POST /api/chat ────────────────► Validators & Prompt Injection Guard
                                             └─► GeminiService (Gemini 2.0 Flash + live context / fallback)
```

### Zero-Config Live Data + Optional Keys
- **Out of the box**: SmogShield queries the free, keyless **Open-Meteo** Geocoding, Air Quality, and Weather APIs for live global readings, and uses its built-in context-grounded response generator when `GEMINI_API_KEY` is not set.
- **With API keys**: Add `GEMINI_API_KEY`, `WAQI_API_TOKEN`, and/or `OPENWEATHER_API_KEY` in `backend/.env` to enable Gemini LLM responses and WAQI/OpenWeatherMap feeds.

---

## 🚀 Quick Start

### Prerequisites
- Python `3.11+`
- Node.js `20+` and `npm`

### 1. Backend Setup

```bash
cd backend
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # Optional: add GEMINI_API_KEY, WAQI_API_TOKEN, OPENWEATHER_API_KEY
uvicorn main:app --reload --port 8000
```

API documentation is available at `http://localhost:8000/api/docs`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. Docker Compose (Optional)

```bash
docker compose up --build
```

---

## 🔒 Security Measures

- **Input Validation & XSS Prevention**: Strict Pydantic field schemas (`models/schemas.py`), city-name regex rejecting path traversal/URLs/scripts (`utils/validators.py`), and safe React rendering without `dangerouslySetInnerHTML`.
- **Prompt Injection Defense**: Delimited `<user_query>` boundary isolation and pattern neutralization before LLM calls.
- **Rate Limiting**: Thread-safe sliding-window rate limiter (`30 req/min` for `/api/chat`, `60 req/min` for AQI/recommendations) returning HTTP `429` with `Retry-After`.
- **Security Headers & CORS**: Attaches `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`, and `Content-Security-Policy`; restricts CORS to configured frontend origins.
- **Secret Hygiene**: All credentials stay in `.env` (excluded via `.gitignore`); unhandled errors return sanitized JSON without stack traces.

---

## ✅ Testing

### Backend Tests & Linting
```bash
cd backend
.venv\Scripts\python.exe -m pytest --cov=. --cov-report=term-missing
.venv\Scripts\python.exe -m ruff check .
```

### Frontend Tests, Linting & Build
```bash
cd frontend
npm run lint
npm test
npm run build
```

### End-to-End Smoke Tests (requires running backend + frontend)
```bash
cd frontend
npm run test:e2e
```

---

## ♿ Accessibility (WCAG 2.1 AA)

- Semantic landmarks (`<header>`, `<aside>`, `<main>`, `<footer>`, `<nav>`) and a keyboard **Skip to main content** link.
- Live AQI status updates announced via `aria-live="polite"`; circular AQI gauge uses `role="meter"` with `aria-valuetext`.
- Status conveyed through both **text badges and color** (never color alone).
- Full keyboard accessibility, visible `:focus-visible` outlines, Dark/Light mode toggle, and `prefers-reduced-motion` support.
- Automated `eslint-plugin-jsx-a11y` checks enforced in CI.

---

## 🤔 Assumptions Made

1. **AQI Standard**: Calculations follow the **US EPA AQI scale (0–500)**, incorporating the 2024 US EPA PM2.5 breakpoint thresholds as a consistent global baseline.
2. **Primary Target Context**: Default presets prioritize winter-smog urban centers (e.g., Delhi, Lahore, Lucknow, Beijing), while city search and GPS work globally.
3. **Advisory Scope**: SmogShield delivers environmental and lifestyle guidance only and does not replace professional medical advice or emergency clinical care.
4. **Connectivity & Free Tier**: Live telemetry relies on internet access to Open-Meteo / WAQI / OpenWeatherMap; when offline, known cities gracefully fall back to curated baseline profiles.
5. **Quantified Impact Estimates**: CO₂ and exposure reduction numbers represent typical urban household estimates (e.g., 12 km daily petrol car vs electric metro commute; HEPA/DIY box-fan CADR efficiency) intended to make behavioral trade-offs concrete.

---

## 📂 Project Structure

```text
SmogShield/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── docs/
│   ├── API.md
│   └── ARCHITECTURE.md
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── middleware/ (cors, rate_limiter, security)
│   │   └── routes/ (health, aqi, recommendations, chat)
│   ├── models/ (enums, schemas)
│   ├── services/ (aqi_service, weather_service, recommendation_engine, gemini_service, cache_service)
│   ├── utils/ (aqi_calculator, constants, validators)
│   └── tests/
└── frontend/
    ├── e2e/smoke.spec.js
    └── src/
        ├── components/ (chat, dashboard, recommendations, layout, common)
        ├── hooks/ (useAQI, useChat, useGeolocation, useLocalStorage)
        ├── services/api.js
        ├── utils/ (accessibility, aqiHelpers, constants)
        └── __tests__/
```

---

## 📄 License

Licensed under the [MIT License](LICENSE).
