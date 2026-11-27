# 🛡️ SmogShield — Urban Air Quality & Winter Smog Assistant

> A GenAI-powered assistant helping families and communities navigate severe winter smog and urban air pollution through low-emission daily routines, room-sized indoor air quality hacks, Dijkstra clean-corridor commute routing, and sustainable alternatives—with quantified health & carbon impact on every choice.

---

## 🎯 Chosen Challenge Vertical

**`[Challenge 6]` Urban Air Quality Assistant (PromptWars Virtual)**

SmogShield is engineered for families, commuters, and neighborhoods impacted by severe winter smog episodes and urban air pollution across South Asia (Delhi, Lahore, Lucknow, Dhaka, Kathmandu) and global cities.

---

## 💡 Approach & Logic

SmogShield pairs **live multi-pollutant telemetry**, **deterministic environmental health engineering**, and **Google Gemini GenAI** in a hybrid architecture:

1. **Live Telemetry & Thermal Inversion Meteorology (`aqi_service.py`, `weather_service.py`)**:
   - Retrieves real-time `PM2.5`, `PM10`, `O₃`, `NO₂`, `SO₂`, `CO`, and a **24-hour diurnal trend** in a single upstream call via **WAQI / OpenWeatherMap** (if keys are configured) or keyless **Open-Meteo** out of the box, with curated urban offline baselines.
   - Evaluates **winter smog-trapping risk** from wind speed (`<7 km/h`), cool temperatures, and humidity.
2. **Household Sensitivity Threshold Shifting (`aqi_calculator.py`)**:
   - Shifts effective AQI risk upward (`+20` to `+60`) for households with children, elderly adults, or respiratory/cardiovascular conditions (`asthma`, `copd`, `heart_disease`).
3. **Pure Environmental Engineering Solvers (`backend/utils/`)**:
   - **Room CADR & Clean-Air Decay Solver (`cadr_calculator.py`)**: Sizes commercial HEPA or low-cost **Corsi-Rosenthal DIY box-fan filters** against the `4.8 ACH` clean-room benchmark and estimates minutes to reach `<15 µg/m³` indoor air.
   - **Dijkstra Clean-Corridor Router (`dijkstra_router.py`)**: Computes the lowest cumulative PM2.5 inhalation route (`Home → Metro Concourse → Greenbelt Path → Work/School`) vs congested arterial corridors.
   - **Commute Inhaled Dose & CO₂ Table (`commute_dose.py`)**: Compares 6 travel modes (`Work From Home`, `Electric Metro`, `Car`, `Motorbike`, `Walk`, `Cycle`) by minute-ventilation PM2.5 inhalation (`µg`) and `kg CO₂` emitted.
4. **Grounded GenAI Conversational Assistant (`gemini_service.py`)**:
   - Injects live AQI, weather dispersion, household profile, and top rule-backed interventions into strictly delimited `<user_query>` prompts for **Google Gemini 2.0 Flash** (`google-genai`), backed by a **SHA-256 AI response cache** and graceful context-grounded fallback when `GEMINI_API_KEY` is omitted.
5. **Community Action & Multilingual Advisories (`CommunityHub.jsx`)**:
   - Interactive neighborhood clean-air pledges tracking collective daily `kg CO₂` and particulate prevention, plus emergency advisories in **English**, **Hindi (`हिन्दी`)**, **Urdu (`اردو` with automatic RTL `dir="rtl"`)**, and **Spanish (`Español`)**.

---

## ⚙️ How the Solution Works

```text
Browser (React 18 + Vite + Tailwind CSS | 66.15 kB gzipped JS)
   ├── Header & Household Sidebar (City/GPS, Light/Dark/High-Contrast OLED, Aa+ Text, Family/Health/Commute)
   ├── Live AQI Dashboard (EPA Meter + Pollutant Cards + Inversion Card + Native SVG 24h Diurnal Sparkline)
   ├── Tabbed Action Plans:
   │      • Daily Routine (Time-window schedule aligned to inversion peaks & midday clearing)
   │      • Indoor Air Hacks (Interactive Room CADR/ACH Solver + DIY Box-Fan & HEPA Guides)
   │      • Clean Commute (Dijkstra Corridor Pathfinder + 6-Mode Inhaled PM2.5 & CO2 Table)
   │      • Sustainable Alternatives (Quantified kg CO2 saved & % exposure reduction)
   │      • Community & Alerts (4-Language RTL Emergency Advisories + Neighborhood Pledges)
   └── SmogShield AI Chat ──► FastAPI Security Pipeline (CORS, GZip, 16KB Cap, Rate Limit, XSS/Injection Guard)
                                └──► GeminiService (SHA-256 LRU Cache + Gemini 2.0 Flash / Rule Fallback)
```

---

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # Optional: add GEMINI_API_KEY, WAQI_API_TOKEN, OPENWEATHER_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                       # Opens http://localhost:5173
```

### Docker Compose
```bash
docker compose up --build
```

---

## 📊 Verification & Evaluation Evidence

Every evaluation focus area is backed by dedicated documentation and verified automation:

| Pillar | Status | Verified Evidence | Doc |
|---|---|---|---|
| **Problem Alignment** | Complete | 8-row Requirements Traceability Matrix covering Challenge 6 | [docs/PROBLEM_ALIGNMENT.md](docs/PROBLEM_ALIGNMENT.md) |
| **Code Quality** | **0 lint errors** | `ruff check .` (0 errors) & `eslint .` (0 errors), modular pure compute | [docs/CODE_QUALITY.md](docs/CODE_QUALITY.md) |
| **Security** | Hardened | `16 KB` cap (`413`), `415` JSON check, rate limit (`429`), CSP/COOP, SHA-256 cache, prompt guard | [docs/SECURITY.md](docs/SECURITY.md) |
| **Efficiency** | Optimized | `66.15 kB` gzip JS, `6.17 kB` gzip CSS, GZip API, 15m LRU+TTL + SHA-256 AI cache | [docs/EFFICIENCY.md](docs/EFFICIENCY.md) |
| **Testing** | **78 / 78 passed** | `60` Pytest (`91%` coverage) + `16` Vitest + `2` Playwright Chrome E2E | [docs/TESTING.md](docs/TESTING.md) |
| **Accessibility** | WCAG AA | Light/Dark/High-Contrast OLED (>14:1), `Aa+` Large Text, `.sr-only` SVG twins, RTL Urdu | [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md) |

---

## 📂 Project Structure

```text
SmogShield/
├── .github/workflows/ci.yml        # Automated CI (Ruff, Pytest, ESLint, Vitest, Build)
├── docs/                           # Architecture, API, & Evaluation Pillar Reports
│   ├── ACCESSIBILITY.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CODE_QUALITY.md
│   ├── EFFICIENCY.md
│   ├── PROBLEM_ALIGNMENT.md
│   ├── SECURITY.md
│   └── TESTING.md
├── backend/                        # FastAPI API, Pure Compute Solvers, & Pytest Suite
│   ├── api/ (middleware, routes)
│   ├── models/ (enums, schemas)
│   ├── services/ (aqi, weather, recommendation, gemini, cache)
│   ├── utils/ (aqi_calculator, cadr_calculator, commute_dose, dijkstra_router, validators)
│   └── tests/
├── frontend/                       # React 18 + Vite + Tailwind CSS UI & Tests
│   ├── e2e/smoke.spec.js
│   └── src/ (components, hooks, services, utils, __tests__)
├── docker-compose.yml
├── metadata.json
├── LICENSE
└── README.md
```

---

## 🤔 Assumptions Made

1. **AQI Baseline**: Computations follow the **US EPA AQI scale (0–500)** using updated 2024 US EPA PM2.5 breakpoint thresholds.
2. **Advisory Scope**: SmogShield offers environmental and lifestyle guidance only and never replaces clinical medical diagnosis.
3. **Connectivity**: Live telemetry queries keyless **Open-Meteo** (or **WAQI** / **OpenWeatherMap** when keys are set) and falls back to curated baseline city profiles if offline.
4. **Impact Estimates**: Commute inhaled PM2.5 (`µg`), CO₂ savings (`kg`), and room CADR decay curves model standard urban indoor infiltration and adult minute-ventilation benchmarks to make everyday trade-offs clear.

---

## 📄 License

Licensed under the [MIT License](LICENSE).
