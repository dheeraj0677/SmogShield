"""Reverse geocoding via Open-Meteo and Nominatim (OpenStreetMap) APIs."""

import httpx


async def reverse_geocode(
    latitude: float, longitude: float, client: httpx.AsyncClient
) -> str | None:
    """Resolve geographic coordinates to a human-readable city name.

    Tries Open-Meteo Geocoding first, then falls back to Nominatim reverse
    geocoding from OpenStreetMap. Returns ``None`` if both services fail.
    """
    # Attempt 1: Open-Meteo nearest-city lookup
    try:
        resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": f"{round(latitude, 2)},{round(longitude, 2)}",
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )
        if resp.status_code == 200:
            results = resp.json().get("results") or []
            if results:
                name = str(results[0].get("name") or "").strip()
                if name:
                    return name
    except (httpx.HTTPError, ValueError, TypeError):
        pass

    # Attempt 2: Nominatim reverse geocoding (OpenStreetMap)
    try:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 10,
                "accept-language": "en",
            },
            headers={"User-Agent": "SmogShield/1.0"},
        )
        if resp.status_code == 200:
            data = resp.json()
            address = data.get("address", {})
            return (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("county")
                or data.get("display_name", "").split(",")[0].strip()
                or None
            )
    except (httpx.HTTPError, ValueError, TypeError):
        pass

    return None


def _is_public_ip(ip: str | None) -> bool:
    """Return True if the IP string looks like a non-private, non-loopback address."""
    if not ip:
        return False
    cleaned = ip.strip()
    if cleaned in {"127.0.0.1", "::1", "localhost", "testclient"}:
        return False
    return not cleaned.startswith(("10.", "192.168.", "172.16.", "172.17.", "172.18."))


async def lookup_ip_location(
    client_ip: str | None, client: httpx.AsyncClient
) -> tuple[float, float, str] | None:
    """Resolve a client IP address to (latitude, longitude, city_name)."""
    ip_segment = client_ip.strip() if _is_public_ip(client_ip) else ""
    urls = [
        f"https://ipwho.is/{ip_segment}",
        f"https://ipapi.co/{ip_segment}/json/" if ip_segment else "https://ipapi.co/json/",
    ]
    for url in urls:
        try:
            resp = await client.get(url, headers={"User-Agent": "SmogShield/1.0"})
            if resp.status_code != 200:
                continue
            data = resp.json()
            if data.get("success") is False or data.get("error"):
                continue
            lat = data.get("latitude")
            lon = data.get("longitude")
            city = str(data.get("city") or data.get("region") or "").strip()
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                return float(lat), float(lon), city or "Your Location"
        except (httpx.HTTPError, ValueError, TypeError):
            continue
    return None
