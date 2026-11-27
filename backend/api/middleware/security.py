"""Security headers, payload size guard, and Content-Type enforcement middleware."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

MAX_JSON_BODY_BYTES = 16 * 1024  # 16 KB cap to prevent payload-flood DoS
API_CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'self';"
UI_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach defensive HTTP security headers to every API and UI response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        is_api = request.url.path.startswith("/api/")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), microphone=(), camera=()"
        )
        response.headers["Content-Security-Policy"] = API_CSP if is_api else UI_CSP
        return response


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Enforce request body size ceiling and JSON Content-Type on POST endpoints."""

    def __init__(self, app, max_bytes: int = MAX_JSON_BODY_BYTES) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "POST" and request.url.path.startswith("/api/"):
            content_type = request.headers.get("content-type", "").lower()
            if "application/json" not in content_type:
                return JSONResponse(
                    status_code=415,
                    content={"detail": "Content-Type must be application/json."},
                )

            content_length = request.headers.get("content-length")
            if (
                content_length
                and content_length.isdigit()
                and int(content_length) > self.max_bytes
            ):
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request payload exceeds {self.max_bytes} byte limit."
                    },
                )

            body = await request.body()
            if len(body) > self.max_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request payload exceeds {self.max_bytes} byte limit."
                    },
                )

        return await call_next(request)
