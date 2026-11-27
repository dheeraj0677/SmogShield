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
