"""Tests for the hybrid RecommendationEngine and /api/recommendations routes."""

from models.enums import AQICategory, BudgetLevel, CommuteType, HomeType
from models.schemas import UserProfile
from services.recommendation_engine import RecommendationEngine
from tests.conftest import make_snapshot


def test_recommendation_engine_low_budget_generates_diy_filter():
    engine = RecommendationEngine()
    snapshot = make_snapshot(city="Delhi", aqi=285, pm25=178.0)
    profile = UserProfile(
        city="Delhi",
        family_members=4,
        has_children=True,
        health_conditions=["asthma"],
        commute_type=CommuteType.CAR,
        home_type=HomeType.APARTMENT,
        has_air_purifier=False,
        budget=BudgetLevel.LOW,
    )

    result = engine.generate(snapshot, profile)

    assert result.effective_aqi > snapshot.aqi
    assert result.total_potential_co2_saved_kg > 0
    assert result.estimated_exposure_reduction_pct >= 50
    assert len(result.schedule) == 4
    hack_titles = [h.title for h in result.indoor_hacks]
    assert any("DIY Box-Fan" in title for title in hack_titles)
    alt_titles = [a.title for a in result.alternatives]
    assert any("Metro/Bus" in title for title in alt_titles)


def test_recommendation_engine_good_air_allows_ventilation():
    engine = RecommendationEngine()
    snapshot = make_snapshot(
        city="London", aqi=32, pm25=6.0, category=AQICategory.GOOD, label="Good"
    )
    profile = UserProfile(city="London", commute_type=CommuteType.PUBLIC_TRANSIT)

    result = engine.generate(snapshot, profile)

    assert result.effective_aqi == 32
    assert any("Cross-ventilate" in item.title for item in result.daily_routine)


def test_recommendations_endpoint_returns_personalized_plan(app, client):
    async def mock_aqi(city: str):
        return make_snapshot(city=city, aqi=220)

    app.state.aqi_service.get_current_aqi = mock_aqi

    response = client.post(
        "/api/recommendations",
        json={
            "city": "Lahore",
            "family_members": 5,
            "has_children": True,
            "has_elderly": True,
            "health_conditions": ["asthma"],
            "commute_type": "motorbike",
            "home_type": "apartment",
            "has_air_purifier": False,
            "budget": "low",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Lahore"
    assert data["effective_aqi"] > 220
    assert len(data["indoor_hacks"]) >= 3
    assert len(data["alternatives"]) >= 2


def test_recommendation_engine_covers_purifier_owner_walk_bike_and_house():
    engine = RecommendationEngine()
    snapshot = make_snapshot(city="Kanpur", aqi=215, pm25=140.0)
    profile = UserProfile(
        city="Kanpur",
        family_members=2,
        has_elderly=True,
        commute_type=CommuteType.WALK_BIKE,
        home_type=HomeType.INDEPENDENT_HOUSE,
        has_air_purifier=True,
        budget=BudgetLevel.HIGH,
    )
    res = engine.generate(snapshot, profile)
    assert any("Optimize existing air purifier" in h.title for h in res.indoor_hacks)
    assert any("enclosed electric transit" in a.title for a in res.alternatives)
    assert any("exterior door thresholds" in h.description for h in res.indoor_hacks)
    assert any(hp.id == "health-action-plan" for hp in res.health_protections)


def test_recommendation_engine_medium_budget_suggests_clean_air_sanctuary():
    engine = RecommendationEngine()
    snapshot = make_snapshot(city="Patna", aqi=165, pm25=90.0)
    profile = UserProfile(
        city="Patna",
        has_air_purifier=False,
        budget=BudgetLevel.MEDIUM,
        commute_type=CommuteType.PUBLIC_TRANSIT,
    )
    res = engine.generate(snapshot, profile)
    assert any("Clean Air Sanctuary" in h.title for h in res.indoor_hacks)
    assert res.effective_aqi == 165

