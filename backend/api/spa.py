"""Same-origin static frontend (SPA) serving for unified production deployments."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

DEFAULT_STATIC_CANDIDATES = (
    Path(__file__).resolve().parents[1] / "static",
    Path(__file__).resolve().parents[2] / "frontend" / "dist",
)


def resolve_static_dir(static_dir: Path | None = None) -> Path | None:
    """Return the first existing built SPA directory containing index.html."""
    candidates = (static_dir,) if static_dir is not None else DEFAULT_STATIC_CANDIDATES
    for candidate in candidates:
        if candidate is not None and (candidate / "index.html").is_file():
            return candidate.resolve()
    return None


def mount_spa(app: FastAPI, static_dir: Path | None = None) -> bool:
    """Attach a path-traversal-safe SPA catch-all route when built assets exist."""
    root = resolve_static_dir(static_dir)
    if root is None:
        return False
    index_file = root / "index.html"

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        cleaned = full_path.lstrip("/")
        if cleaned == "api" or cleaned.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found.")

        if cleaned:
            target = (root / cleaned).resolve()
            if target.is_relative_to(root) and target.is_file():
                rel_parts = target.relative_to(root).parts
                if not any(part.startswith(".") for part in rel_parts):
                    return FileResponse(target)

        return FileResponse(index_file)

    return True
