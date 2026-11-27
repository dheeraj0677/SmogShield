"""Inhaled PM2.5 particulate dose and CO2 emission calculations across commute modes."""

# Minute ventilation (m³/min), cabin/mask penetration factor, and CO2 kg/km
_MODE_PROFILES: dict[str, dict] = {
    "work_from_home": {
        "label": "Work From Home (Indoor Filtered)",
        "ventilation_m3_min": 0.008,
        "exposure_factor": 0.22,
        "co2_kg_per_km": 0.0,
        "speed_kmh": 1.0,
    },
    "public_transit": {
        "label": "Electric Metro / AC Bus",
        "ventilation_m3_min": 0.010,
        "exposure_factor": 0.45,
        "co2_kg_per_km": 0.035,
        "speed_kmh": 28.0,
    },
    "car": {
        "label": "Private Car (Recirculation AC)",
        "ventilation_m3_min": 0.009,
        "exposure_factor": 0.58,
        "co2_kg_per_km": 0.192,
        "speed_kmh": 24.0,
    },
    "motorbike": {
        "label": "Two-Wheeler / Motorbike",
        "ventilation_m3_min": 0.014,
        "exposure_factor": 1.25,
        "co2_kg_per_km": 0.103,
        "speed_kmh": 26.0,
    },
    "walk": {
        "label": "Roadside Walking (Unmasked)",
        "ventilation_m3_min": 0.024,
        "exposure_factor": 1.0,
        "co2_kg_per_km": 0.0,
        "speed_kmh": 4.8,
    },
    "walk_bike": {
        "label": "Cycling (Unmasked)",
        "ventilation_m3_min": 0.042,
        "exposure_factor": 1.15,
        "co2_kg_per_km": 0.0,
        "speed_kmh": 15.0,
    },
}


def compute_commute_comparison(
    distance_km: float,
    ambient_pm25: float,
    wear_n95_mask: bool = False,
) -> list[dict]:
    """Compare round-trip inhaled PM2.5 (µg) and CO2 emissions (kg) for commute modes."""
    round_trip_km = max(1.0, distance_km * 2.0)
    mask_multiplier = 0.25 if wear_n95_mask else 1.0

    results: list[dict] = []
    baseline_dose = None

    for mode_id, cfg in _MODE_PROFILES.items():
        if mode_id == "work_from_home":
            duration_min = 45.0
            effective_mask = 1.0
        else:
            duration_min = (round_trip_km / cfg["speed_kmh"]) * 60.0
            effective_mask = (
                mask_multiplier
                if mode_id in {"walk", "walk_bike", "motorbike", "public_transit"}
                else 1.0
            )

        inhaled_ug = round(
            ambient_pm25
            * cfg["exposure_factor"]
            * effective_mask
            * cfg["ventilation_m3_min"]
            * duration_min,
            1,
        )
        co2_kg = round(round_trip_km * cfg["co2_kg_per_km"], 2)

        if mode_id == "motorbike":
            baseline_dose = inhaled_ug

        results.append(
            {
                "mode": mode_id,
                "label": cfg["label"],
                "duration_min": int(round(duration_min)),
                "inhaled_pm25_ug": inhaled_ug,
                "co2_kg": co2_kg,
                "recommended": inhaled_ug <= (ambient_pm25 * 0.45),
            }
        )

    ref_dose = baseline_dose or max(item["inhaled_pm25_ug"] for item in results) or 1.0
    for item in results:
        reduction = max(0, int(round((1.0 - (item["inhaled_pm25_ug"] / ref_dose)) * 100)))
        item["exposure_vs_peak_pct"] = reduction

    results.sort(key=lambda r: r["inhaled_pm25_ug"])
    return results
