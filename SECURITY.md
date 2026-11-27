# Security Architecture & OWASP Defense — SmogShield

## Defense-in-Depth Controls

| Threat / Standard | Control Implemented | Source Location | Verification |
|---|---|---|---|
| **API Key Exposure (OWASP A02 / CWE-798)** | `GEMINI_API_KEY`, `WAQI_API_TOKEN`, and `OPENWEATHER_API_KEY` are loaded server-side only; zero secrets in `frontend/` or git history (`.env` in `.gitignore`). | `backend/config.py`, `.gitignore` | `backend/tests/test_security.py` |
| **XSS & HTML Injection (CWE-79)** | `sanitize_text()` strips HTML tags, control chars, and event attributes; `validate_city_name()` rejects `<`, `>`, `;`, `/`, `\`, `..`, URLs before sanitization; React renders formatted text without `dangerouslySetInnerHTML`. | `backend/utils/validators.py`, `frontend/src/components/chat/MessageBubble.jsx` | `backend/tests/test_validators.py` |
| **Prompt Injection & System Prompt Leakage** | Untrusted user text isolated inside `<user_query>` boundary delimiters; override directives neutralized (`detect_prompt_injection`, `neutralize_prompt_injection`); `_contains_prompt_leak()` blocks boundary leakage in responses. | `backend/services/gemini_service.py`, `backend/utils/validators.py` | `backend/tests/test_chat.py`, `backend/tests/test_validators.py` |
| **Payload DoS & Wrong Media Type (CWE-770)** | `MaxBodySizeMiddleware` enforces a `16 KB` cap on POST payloads (HTTP `413`) and requires `application/json` (HTTP `415`). | `backend/api/middleware/security.py` | `backend/tests/test_security.py` |
| **Brute-Force / Quota Abuse (OWASP A04)** | Thread-safe `SlidingWindowRateLimiter` limits `/api/chat` (`30 req/min`) and AQI/recommendation routes (`60 req/min`) per IP with `Retry-After` and `X-RateLimit-*` headers. | `backend/api/middleware/rate_limiter.py` | `backend/tests/test_security.py` |
| **PII-Free AI Caching** | `TTLCache.hash_key()` hashes normalized context with **SHA-256** so raw user query strings are not stored as plain keys in memory maps. | `backend/services/cache_service.py` | `backend/tests/test_compute_tools.py` |
| **Security Headers & CORS** | `SecurityHeadersMiddleware` sets `CSP`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `X-Permitted-Cross-Domain-Policies`, and `Permissions-Policy`; CORS allows configured origins only. | `backend/api/middleware/security.py`, `backend/api/middleware/cors.py` | `backend/tests/test_security.py` |
| **Error Sanitization (CWE-209)** | Global FastAPI exception handler logs internally and returns generic JSON error responses without stack traces. | `backend/main.py` | `backend/tests/test_security.py` |
