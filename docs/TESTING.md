# Automated Testing & Verification Report — SmogShield

**Total Verified Passing Tests:** **108 / 108 (100% Passing)**  
**Backend Statement Coverage:** **97%** (`2,039` statements) | **Frontend `src/` Coverage:** **97.08%** (`v8`)

---

## 1. Backend Verification (`Pytest` + `Ruff`)

- **Linter**: `ruff check .` — **0 errors**
- **Test Runner**: `pytest --cov=. --cov-report=term-missing` — **79 / 79 passed** (`4.07s`)

| Test File                              | Focus                                                                                                                                                                     | Tests | Coverage Highlights                                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | --------------------------------------------------------------------------------------------------- |
| `backend/tests/test_validators.py`     | XSS stripping, path traversal rejection, prompt-injection neutralization, EPA breakpoints (`PM2.5`, `PM10`, `O3`, `NO2`, `SO2`, `CO`)                                     | 28    | `utils/aqi_calculator.py` (95%), `utils/validators.py` (91%)                                        |
| `backend/tests/test_compute_tools.py`  | Room CADR/ACH decay solver, commute PM2.5 dose/CO₂, Dijkstra clean corridor, SHA-256 cache eviction, `/api/tools/*`                                                       | 11    | `utils/cadr_calculator.py` (100%), `utils/commute_dose.py` (100%), `utils/dijkstra_router.py` (93%) |
| `backend/tests/test_security.py`       | Security headers (`CSP`, `COOP`, `nosniff`, `DENY`), SPA path-traversal guard, Render CORS, rate limit (`429`), `16 KB` cap (`413`), JSON guard (`415`), SHA-256 AI cache | 8     | `api/middleware/security.py` (97%), `api/spa.py` (93%), `rate_limiter.py` (94%)                     |
| `backend/tests/test_aqi_service.py`    | Google Air Quality API v1, Open-Meteo & OpenWeatherMap HTTP parsing, TTL caching, `404` unknown city, offline fallback                                                    | 6     | `services/open_meteo_aqi.py` (100%), `weather_service.py` (86%)                                     |
| `backend/tests/test_recommendation.py` | Sensitive household risk adjustment, DIY box-fan vs HEPA optimization, daily schedule generation                                                                          | 5     | `services/recommendation_engine.py` + `recommendations/*` (100%)                                    |
| `backend/tests/test_chat.py`           | Grounded `/api/chat`, OpenRouter `:free`-only enforcement & null fallback, Gemini fallback, XSS rejection (`422`), prompt-leak guard                                      | 7     | `services/gemini_service.py` (95%), `fallback_responder.py` (100%)                                  |

---

## 2. Frontend Verification (`ESLint` + `Vitest` + `Playwright` + `Axe`)

- **Linter**: `npm run lint` (`eslint` + `eslint-plugin-jsx-a11y`) — **0 errors**
- **Unit & DOM Tests**: `npm run test:coverage` (`vitest` + `v8`) — **27 / 27 passed** (`97.08%` `src/` coverage)
- **Production Build**: `npm run build` (`vite build`) — `70.61 kB` gzipped JS, `7.76 kB` gzipped CSS
- **Browser E2E + WCAG Scan**: `npx playwright test` (real headless Chrome + `@axe-core/playwright`) — **2 / 2 passed** (`21.4s`, **`0` WCAG 2.1 A/AA violations**):
  - Full desktop flow: live AQI meter, 24h diurnal sparkline, CADR solver, Dijkstra clean corridor, Urdu RTL community alerts, AI chat submission.
  - Mobile responsive viewport (`390×844`) layout and drawer toggle.
