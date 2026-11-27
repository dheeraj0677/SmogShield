"""Pure room-level Clean Air Delivery Rate (CADR) and ACH decay engineering helpers."""

import math


def compute_cadr_analysis(
    room_area_sqft: float,
    ceiling_height_ft: float,
    outdoor_pm25: float,
    purifier_cadr_m3h: float,
    seal_quality: str = "average",
) -> dict:
    """Compute Air Changes per Hour (ACH), recommended CADR, and decay time to <15 µg/m³."""
    area_sqm = max(4.0, room_area_sqft * 0.092903)
    height_m = max(2.0, ceiling_height_ft * 0.3048)
    room_volume_m3 = round(area_sqm * height_m, 2)

    ach = round(purifier_cadr_m3h / room_volume_m3, 2)
    recommended_cadr_4_8_ach = round(room_volume_m3 * 4.8, 1)

    infiltration_factor = {"tight": 0.25, "average": 0.45, "leaky": 0.70}.get(
        seal_quality, 0.45
    )
    initial_indoor_pm25 = round(max(12.0, outdoor_pm25 * infiltration_factor), 1)
    target_pm25 = 15.0

    # First-order exponential decay considering infiltration baseline
    steady_state_pm25 = round(
        (outdoor_pm25 * infiltration_factor * 0.5) / max(0.5, ach + 0.5), 1
    )

    if initial_indoor_pm25 <= target_pm25 or ach <= 0.1:
        minutes_to_safe = 0 if initial_indoor_pm25 <= target_pm25 else 240
    else:
        effective_ach = max(0.2, ach)
        hours = math.log(initial_indoor_pm25 / target_pm25) / effective_ach
        minutes_to_safe = min(240, max(5, int(round(hours * 60))))

    meets_who_target = ach >= 4.8
    efficiency_note = (
        f"Achieves {ach} ACH (meets ≥4.8 ACH clean-air sanctuary standard)."
        if meets_who_target
        else (
            f"Current {ach} ACH is below the 4.8 ACH clean-room benchmark; "
            f"aim for ≥{recommended_cadr_4_8_ach} m³/h CADR or run a second DIY box-fan filter."
        )
    )

    return {
        "room_volume_m3": room_volume_m3,
        "ach": ach,
        "recommended_cadr_m3h": recommended_cadr_4_8_ach,
        "initial_indoor_pm25": initial_indoor_pm25,
        "projected_steady_pm25": steady_state_pm25,
        "minutes_to_safe_air": minutes_to_safe,
        "meets_target_ach": meets_who_target,
        "efficiency_note": efficiency_note,
    }
