# Problem Statement Alignment & Requirements Traceability Matrix (RTM)

**Challenge Vertical:** `[Challenge 6] Urban Air Quality Assistant`  
**Solution:** **SmogShield**

---

## 1. Challenge Alignment Summary

> *"Create a GenAI-powered assistant that helps families and communities navigate severe winter smog and urban air pollution. The application should suggest low-emission daily routines, indoor air quality hacks, and sustainable alternatives tailored to their location and lifestyle, while clearly explaining the direct impact of their choices."*

SmogShield addresses every dimension of Challenge 6 with live telemetry, deterministic environmental engineering models, and context-grounded Generative AI.

---

## 2. Requirements Traceability Matrix (RTM)

| Req ID | Challenge Requirement | Implementation | Verification |
|---|---|---|---|
| **REQ-01** | Live urban air quality & winter smog tracking by city or GPS | `backend/services/aqi_service.py`, `backend/services/weather_service.py`, `frontend/src/components/dashboard/AQIDashboard.jsx` | `backend/tests/test_aqi_service.py`, `frontend/src/__tests__/AQIDashboard.test.jsx` |
| **REQ-02** | 24-hour diurnal smog cycle & thermal inversion risk assessment | `backend/services/aqi_service.py`, `frontend/src/components/dashboard/SmogSparkline.jsx`, `WeatherCard.jsx` | `backend/tests/test_aqi_service.py`, `frontend/src/__tests__/NewFeatures.test.jsx` |
| **REQ-03** | Low-emission daily routines tailored to location & household profile | `backend/services/recommendation_engine.py`, `frontend/src/components/recommendations/DailyRoutine.jsx` | `backend/tests/test_recommendation.py`, `frontend/src/__tests__/Components.test.jsx` |
| **REQ-04** | Practical indoor air quality hacks + Room CADR/ACH & DIY box-fan solver | `backend/utils/cadr_calculator.py`, `frontend/src/components/recommendations/CADRCalculator.jsx`, `IndoorHacks.jsx` | `backend/tests/test_compute_tools.py`, `frontend/src/__tests__/NewFeatures.test.jsx` |
| **REQ-05** | Sustainable alternatives & Dijkstra clean-corridor commute planner | `backend/utils/dijkstra_router.py`, `backend/utils/commute_dose.py`, `frontend/src/components/recommendations/TransitPlanner.jsx` | `backend/tests/test_compute_tools.py`, `frontend/src/__tests__/NewFeatures.test.jsx` |
| **REQ-06** | Direct impact explanation (CO₂ saved & PM2.5 exposure reduction) | `backend/services/recommendation_engine.py`, `ImpactMeter.jsx`, `MessageBubble.jsx` | `backend/tests/test_recommendation.py`, `frontend/src/__tests__/Components.test.jsx` |
| **REQ-07** | GenAI conversational assistant grounded in live AQI & user context | `backend/services/gemini_service.py`, `backend/api/routes/chat.py`, `frontend/src/components/chat/ChatWindow.jsx` | `backend/tests/test_chat.py`, `frontend/src/__tests__/ChatWindow.test.jsx` |
| **REQ-08** | Community action pledges & multilingual emergency advisories | `frontend/src/components/recommendations/CommunityHub.jsx`, `frontend/src/utils/translations.js` | `frontend/src/__tests__/NewFeatures.test.jsx`, `frontend/e2e/smoke.spec.js` |
