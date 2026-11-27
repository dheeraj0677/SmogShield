# Google Services Integration — SmogShield

## Integrated Google Ecosystem Technologies

1. **Google Gemini (`google-genai` SDK — Gemini 2.0 Flash)**
   - **Location**: [backend/services/llm_providers.py](../backend/services/llm_providers.py), [backend/services/gemini_service.py](../backend/services/gemini_service.py)
   - **Role**: Server-side GenAI advisor generating household-specific smog protection plans grounded in delimited `<environment_context>` and `<household_profile>` telemetry.
2. **Google Gemma 4 Open Weights (`google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free`)**
   - **Location**: [backend/services/llm_providers.py](../backend/services/llm_providers.py)
   - **Role**: Free-tier open-weight Google LLM inference via OpenRouter with `:free`-only enforcement and automatic failover.
3. **Google Air Quality API v1 (`airquality.googleapis.com/v1/currentConditions:lookup`)**
   - **Location**: [backend/services/aqi_providers.py](../backend/services/aqi_providers.py), [backend/services/aqi_service.py](../backend/services/aqi_service.py)
   - **Role**: Optional first-class hyperlocal pollutant retrieval when `GOOGLE_AIR_QUALITY_API_KEY` is configured, normalized seamlessly alongside WAQI and Open-Meteo.
4. **Google Fonts (`Inter`, `JetBrains Mono`, `Noto Sans Arabic`)**
   - **Location**: [frontend/index.html](../frontend/index.html)
   - **Role**: Clean high-legibility UI typography, monospace numeric readouts, and native RTL Urdu script rendering.
5. **Google Chrome Browser Automation & Accessibility Verification**
   - **Location**: [frontend/playwright.config.js](../frontend/playwright.config.js), [frontend/e2e/smoke.spec.js](../frontend/e2e/smoke.spec.js)
   - **Role**: Real-browser E2E smoke testing and automated `@axe-core/playwright` WCAG 2.1 AA compliance scanning.
