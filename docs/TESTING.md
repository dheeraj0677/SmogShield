# Automated Testing & Verification Report — SmogShield

**Total Verified Passing Tests:** **83 / 83 (100% Passing)**  
**Backend Statement Coverage:** **91%** (`1,623` statements across backend)

---

## 1. Backend Verification (`Pytest` + `Ruff`)

- **Linter**: `ruff check .` — **0 errors**
- **Test Runner**: `pytest --cov=. --cov-report=term-missing` — **62 / 62 passed** (`0.87s`)

| Test File | Focus | Tests | Coverage Highlights |
|---|---|---|---|
| `backend/tests/test_validators.py` | XSS stripping, path traversal rejection, prompt-injection neutralization, EPA breakpoints (`PM2.5`, `PM10`, `O3`, `NO2`, `SO2`, `CO`) | 28 | `utils/aqi_calculator.py` (95%), `utils/validators.py` (91%) |
| `backend/tests/test_compute_tools.py` | Room CADR/ACH decay solver, commute PM2.5 dose/CO₂, Dijkstra clean corridor, SHA-256 cache eviction, `/api/tools/*` | 11 | `utils/cadr_calculator.py` (100%), `utils/commute_dose.py` (100%), `utils/dijkstra_router.py` (93%) |
| `backend/tests/test_security.py` | Security headers (`CSP`, `COOP`, `nosniff`, `DENY`), sliding-window rate limit (`429`), `16 KB` cap (`413`), JSON guard (`415`), CORS, SHA-256 AI cache | 6 | `api/middleware/security.py` (97%), `rate_limiter.py` (94%) |
| `backend/tests/test_aqi_service.py` | Open-Meteo & OpenWeatherMap mock HTTP parsing, TTL caching, `404` unknown city, offline baseline fallback, API routes | 5 | `services/weather_service.py` (86%) |
| `backend/tests/test_recommendation.py` | Sensitive household risk adjustment, DIY box-fan vs HEPA optimization, daily schedule generation | 5 | `services/recommendation_engine.py` (100%) |
| `backend/tests/test_chat.py` | Grounded `/api/chat`, OpenRouter `:free`-only enforcement & null fallback, Gemini fallback, XSS rejection (`422`), prompt-leak guard | 7 | `services/gemini_service.py` (87%) |

---

## 2. Frontend Verification (`ESLint` + `Vitest` + `Playwright`)

- **Linter**: `npm run lint` (`eslint` + `eslint-plugin-jsx-a11y`) — **0 errors**
- **Unit & DOM Tests**: `npm test` (`vitest run` + `@testing-library/react`) — **19 / 19 passed** across 5 suites
- **Production Build**: `npm run build` (`vite build`) — `70.61 kB` gzipped JS, `7.85 kB` gzipped CSS
- **Browser E2E**: `npx playwright test` (real headless Chrome against live FastAPI + Vite) — **2 / 2 passed** (`6.4s`):
  - Full desktop flow: live AQI meter, 24h diurnal sparkline, CADR solver, Dijkstra clean corridor, Urdu RTL community alerts, AI chat submission.
  - Mobile responsive viewport (`390×844`) layout and drawer toggle.
