# Code Quality & Engineering Standards — SmogShield

## Architectural Separation of Concerns

- **Pure Domain Compute (`backend/utils/`)**: EPA AQI breakpoints (`aqi_calculator.py`), Room CADR/ACH decay math (`cadr_calculator.py`), Commute inhaled PM2.5 dose (`commute_dose.py`), Dijkstra clean-corridor pathfinder (`dijkstra_router.py`), and validators (`validators.py`) have zero framework/HTTP side effects.
- **Service Layer (`backend/services/`)**: `AQIService`, `WeatherService`, `RecommendationEngine`, `GeminiService`, and `TTLCache` encapsulate external integrations, fallback logic, and caching.
- **API Layer (`backend/api/`)**: Thin FastAPI routers (`routes/`) validate inputs via Pydantic v2 models (`models/schemas.py`) and delegate work to services.
- **Modular React UI (`frontend/src/`)**: Clean separation across `hooks/`, `services/api.js`, `utils/`, and `components/{chat,dashboard,recommendations,layout,common}`.

## Static Analysis & Type Safety

- **Backend**:
  - Enforced with **Ruff** (`pyproject.toml`: `E`, `F`, `I`, `W`, `B`, `S` Bandit security rules, max line length `100`).
  - Strict **Pydantic v2** schemas and **Python Enums** for all request/response contracts.
- **Frontend**:
  - Enforced with **ESLint** (`eslint.config.js`), **`eslint-plugin-react-hooks`**, and **`eslint-plugin-jsx-a11y`**.
  - Performance-critical chart components wrapped with `React.memo`.
  - Standardized formatting via `.editorconfig`.
