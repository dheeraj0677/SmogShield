"""Tests for CADR room air decay, commute inhaled dose, Dijkstra routing, and tool APIs."""

from services.cache_service import TTLCache
from tests.conftest import make_snapshot
from utils.cadr_calculator import compute_cadr_analysis
from utils.commute_dose import compute_commute_comparison
from utils.dijkstra_router import find_cleanest_corridor


def test_cadr_calculator_achieves_target_for_appropriately_sized_purifier():
    res = compute_cadr_analysis(
        room_area_sqft=150,
        ceiling_height_ft=9,
        outdoor_pm25=200,
        purifier_cadr_m3h=280,
        seal_quality="tight",
    )
    assert res["room_volume_m3"] > 30
    assert res["ach"] >= 4.8
    assert res["meets_target_ach"] is True
    assert res["minutes_to_safe_air"] > 0
    assert res["projected_steady_pm25"] < res["initial_indoor_pm25"]


def test_cadr_calculator_flags_undersized_purifier_in_leaky_room():
    res = compute_cadr_analysis(
        room_area_sqft=320,
        ceiling_height_ft=10,
        outdoor_pm25=220,
        purifier_cadr_m3h=120,
        seal_quality="leaky",
    )
    assert res["ach"] < 4.8
    assert res["meets_target_ach"] is False
    assert "below the 4.8 ACH" in res["efficiency_note"]


def test_commute_comparison_shows_n95_and_metro_dose_reductions():
    unmasked = compute_commute_comparison(distance_km=10, ambient_pm25=180, wear_n95_mask=False)
    masked = compute_commute_comparison(distance_km=10, ambient_pm25=180, wear_n95_mask=True)

    by_mode_unmasked = {item["mode"]: item for item in unmasked}
    by_mode_masked = {item["mode"]: item for item in masked}

    assert by_mode_unmasked["work_from_home"]["co2_kg"] == 0.0
    assert (
        by_mode_unmasked["public_transit"]["inhaled_pm25_ug"]
        < by_mode_unmasked["motorbike"]["inhaled_pm25_ug"]
    )
    assert (
        by_mode_masked["walk_bike"]["inhaled_pm25_ug"]
        < by_mode_unmasked["walk_bike"]["inhaled_pm25_ug"]
    )


def test_dijkstra_cleanest_corridor_beats_arterial_route():
    result = find_cleanest_corridor(ambient_aqi=260, ambient_pm25=175.0, distance_km=8.0)
    clean = result["cleanest_route"]
    arterial = result["standard_arterial"]

    assert clean["path"][0] == "Home"
    assert clean["path"][-1] == "Work / School"
    assert clean["inhaled_pm25_ug"] < arterial["inhaled_pm25_ug"]
    assert result["pm25_dose_saved_ug"] > 0
    assert result["exposure_reduction_pct"] > 30


def test_tools_endpoints_and_cache_stats(app, client):
    async def mock_aqi(city: str):
        return make_snapshot(city=city, aqi=245, pm25=168.0)

    app.state.aqi_service.get_current_aqi = mock_aqi

    cadr_res = client.post(
        "/api/tools/cadr",
        json={
            "room_area_sqft": 180,
            "ceiling_height_ft": 9.5,
            "outdoor_pm25": 168,
            "purifier_cadr_m3h": 250,
            "seal_quality": "average",
        },
    )
    assert cadr_res.status_code == 200
    assert cadr_res.json()["recommended_cadr_m3h"] > 0

    commute_res = client.post(
        "/api/tools/commute-plan",
        json={"city": "Delhi", "distance_km": 10.0, "wear_n95_mask": True},
    )
    assert commute_res.status_code == 200
    data = commute_res.json()
    assert data["city"] == "Delhi"
    assert len(data["mode_comparisons"]) == 6
    assert data["corridor_analysis"]["exposure_reduction_pct"] > 20

    stats_res = client.get("/api/tools/cache-stats")
    assert stats_res.status_code == 200
    assert "ai_response_cache" in stats_res.json()


def test_ttl_cache_sha256_hash_key_and_lru_eviction():
    cache = TTLCache(ttl_seconds=60, max_entries=2)
    k1 = TTLCache.hash_key("chat", {"q": "mask"})
    k2 = TTLCache.hash_key("chat", {"q": "purifier"})
    k3 = TTLCache.hash_key("chat", {"q": "commute"})

    assert "mask" not in k1
    cache.set(k1, "a")
    cache.set(k2, "b")
    assert cache.get(k1) == "a"  # touch k1 so k2 becomes LRU
    cache.set(k3, "c")
    assert cache.get(k2) is None
    assert cache.get(k1) == "a"
    assert cache.stats()["size"] == 2


def test_cadr_handles_clean_room_and_extreme_bounds():
    clean = compute_cadr_analysis(
        room_area_sqft=100,
        ceiling_height_ft=8,
        outdoor_pm25=20,
        purifier_cadr_m3h=250,
        seal_quality="tight",
    )
    assert clean["minutes_to_safe_air"] == 0
    assert clean["meets_target_ach"] is True


def test_dijkstra_scales_across_short_and_long_commutes():
    short_trip = find_cleanest_corridor(ambient_aqi=180, ambient_pm25=95.0, distance_km=3.0)
    long_trip = find_cleanest_corridor(ambient_aqi=180, ambient_pm25=95.0, distance_km=20.0)
    assert long_trip["pm25_dose_saved_ug"] > short_trip["pm25_dose_saved_ug"]
    assert (
        short_trip["cleanest_route"]["duration_min"]
        < long_trip["cleanest_route"]["duration_min"]
    )


def test_cadr_handles_leaky_room_and_high_seal():
    leaky = compute_cadr_analysis(
        room_area_sqft=200,
        ceiling_height_ft=10,
        outdoor_pm25=200,
        purifier_cadr_m3h=240,
        seal_quality="leaky",
    )
    tight = compute_cadr_analysis(
        room_area_sqft=200,
        ceiling_height_ft=10,
        outdoor_pm25=200,
        purifier_cadr_m3h=240,
        seal_quality="tight",
    )
    assert leaky["initial_indoor_pm25"] > tight["initial_indoor_pm25"]
    assert leaky["projected_steady_pm25"] > tight["projected_steady_pm25"]


def test_commute_comparison_ranks_wfh_lowest_dose():
    modes = compute_commute_comparison(distance_km=12, ambient_pm25=210, wear_n95_mask=False)
    assert modes[0]["mode"] == "work_from_home"
    assert modes[-1]["inhaled_pm25_ug"] > modes[0]["inhaled_pm25_ug"]


def test_commute_plan_returns_400_for_invalid_city_and_404_for_unknown(app, client):
    from services.aqi_service import CityNotFoundError

    async def mock_aqi(city: str):
        raise CityNotFoundError("Unknown")

    app.state.aqi_service.get_current_aqi = mock_aqi

    res_400 = client.post(
        "/api/tools/commute-plan",
        json={"city": "Bad<script>", "distance_km": 5},
    )
    assert res_400.status_code in (400, 422)

    res_404 = client.post(
        "/api/tools/commute-plan",
        json={"city": "UnknownCityXYZ", "distance_km": 5},
    )
    assert res_404.status_code == 404

