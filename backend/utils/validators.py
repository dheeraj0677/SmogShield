"""Input sanitization, city validation, and prompt injection guardrails."""

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE_RE = re.compile(r"\s+")
_CITY_NAME_RE = re.compile(r"^[A-Za-zÀ-ÿ0-9\s,.\-']{2,80}$")

# Common prompt injection patterns to neutralize before passing user text to LLMs
_INJECTION_PATTERNS = [
    re.compile(
        r"ignore\s+(all\s+|any\s+)?(previous|prior|above)\s+instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"(reveal|print|show|output)\s+(your\s+)?(system\s+prompt|instructions)",
        re.IGNORECASE,
    ),
    re.compile(r"you\s+are\s+now\s+(dan|unrestricted|jailbroken)", re.IGNORECASE),
    re.compile(r"<\s*/?\s*(system|assistant|developer|user_query)\s*>", re.IGNORECASE),
]


def sanitize_text(value: str, max_length: int = 1500) -> str:
    """Strip HTML tags, control characters, and dangerous payloads from text."""
    if not isinstance(value, str):
        return ""
    cleaned = _CONTROL_CHARS_RE.sub("", value)
    cleaned = _HTML_TAG_RE.sub(" ", cleaned)
    cleaned = cleaned.replace("javascript:", "").replace("onerror=", "").replace("onload=", "")
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned[:max_length]


def validate_city_name(city: str) -> str:
    """Validate and normalize a city query string, rejecting injection or path traversal."""
    if not isinstance(city, str):
        raise ValueError("City name must be a string.")
    if any(ch in city for ch in ("<", ">", "/", "\\", ";")) or ".." in city:
        raise ValueError("City name contains disallowed characters.")
    cleaned = sanitize_text(city, max_length=80)
    if not cleaned:
        raise ValueError("City name cannot be empty.")
    if "http" in cleaned.lower():
        raise ValueError("City name contains disallowed characters.")
    if not _CITY_NAME_RE.match(cleaned):
        raise ValueError(
            "City name must be 2-80 characters using letters, spaces, commas, hyphens, or dots."
        )
    return cleaned


def detect_prompt_injection(text: str) -> bool:
    """Return True if input text matches known prompt-override heuristics."""
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)


def neutralize_prompt_injection(text: str) -> str:
    """Redact delimiter tags and flag suspicious override instructions safely."""
    sanitized = sanitize_text(text)
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub("[filtered-directive]", sanitized)
    return sanitized
