"""Dijkstra clean-corridor pathfinder minimizing cumulative inhaled PM2.5 exposure."""

import heapq


def find_cleanest_corridor(
    ambient_aqi: int,
    ambient_pm25: float,
    distance_km: float = 8.0,
) -> dict:
    """Compare arterial rush-hour route vs green/metro clean corridor via Dijkstra's algorithm."""
    scale = max(0.4, distance_km / 8.0)

    # Directed graph nodes: Origin -> intermediate junctions -> Destination
    # Each edge carries: (neighbor, minutes, pm25_multiplier, road_type)
    graph: dict[str, list[tuple[str, float, float, str]]] = {
        "Home": [
            ("Diesel Arterial A", round(11 * scale, 1), 1.45, "Heavy Traffic Arterial"),
            ("Residential Lane", round(13 * scale, 1), 0.90, "Quiet Side Street"),
            ("Metro Concourse", round(9 * scale, 1), 0.42, "Electric Underground Metro"),
        ],
        "Diesel Arterial A": [
            ("Ring Road Junction", round(10 * scale, 1), 1.55, "Idling Bottleneck"),
            ("Greenbelt Path", round(12 * scale, 1), 0.72, "Tree-Buffered Path"),
        ],
        "Residential Lane": [
            ("Greenbelt Path", round(10 * scale, 1), 0.68, "Tree-Buffered Path"),
            ("Ring Road Junction", round(11 * scale, 1), 1.30, "Mixed Arterial"),
        ],
        "Metro Concourse": [
            ("Greenbelt Path", round(8 * scale, 1), 0.48, "Electric Metro + Shaded Walk"),
        ],
        "Ring Road Junction": [
            ("Work / School", round(9 * scale, 1), 1.40, "Congested Corridor"),
        ],
        "Greenbelt Path": [
            ("Work / School", round(8 * scale, 1), 0.62, "Low-Emission Green Corridor"),
        ],
        "Work / School": [],
    }

    def _dijkstra(optimize_for: str) -> dict:
        """Run Dijkstra shortest-path search optimizing either dose or travel time."""
        # Weight is either cumulative exposure dose proxy or travel minutes
        pq: list[tuple[float, str, float, float, list[str]]] = [
            (0.0, "Home", 0.0, 0.0, ["Home"])
        ]
        best_cost: dict[str, float] = {"Home": 0.0}

        while pq:
            cost, node, total_min, total_exposure, path = heapq.heappop(pq)
            if node == "Work / School":
                baseline = max(1.0, total_min * ambient_pm25 * 0.015)
                return {
                    "strategy": optimize_for,
                    "path": path,
                    "duration_min": int(round(total_min)),
                    "inhaled_pm25_ug": round(total_exposure, 1),
                    "avg_corridor_aqi": int(round(ambient_aqi * (total_exposure / baseline))),
                }
            if cost > best_cost.get(node, float("inf")):
                continue

            for nxt, mins, mult, _road in graph.get(node, []):
                # 0.015 m³/min average commute breathing rate
                seg_exposure = ambient_pm25 * mult * 0.015 * mins
                step_weight = seg_exposure if optimize_for == "lowest_exposure" else mins
                new_cost = cost + step_weight
                if new_cost < best_cost.get(nxt, float("inf")):
                    best_cost[nxt] = new_cost
                    heapq.heappush(
                        pq,
                        (
                            new_cost,
                            nxt,
                            total_min + mins,
                            total_exposure + seg_exposure,
                            [*path, nxt],
                        ),
                    )
        return {}

    cleanest = _dijkstra("lowest_exposure")
    arterial = {
        "strategy": "standard_arterial",
        "path": ["Home", "Diesel Arterial A", "Ring Road Junction", "Work / School"],
        "duration_min": int(round((11 + 10 + 9) * scale)),
        "inhaled_pm25_ug": round(
            ambient_pm25 * 0.015 * ((11 * 1.45 + 10 * 1.55 + 9 * 1.40) * scale), 1
        ),
    }

    saved_ug = round(max(0.0, arterial["inhaled_pm25_ug"] - cleanest["inhaled_pm25_ug"]), 1)
    reduction_pct = (
        int(round((saved_ug / arterial["inhaled_pm25_ug"]) * 100))
        if arterial["inhaled_pm25_ug"] > 0
        else 0
    )

    return {
        "cleanest_route": cleanest,
        "standard_arterial": arterial,
        "pm25_dose_saved_ug": saved_ug,
        "exposure_reduction_pct": reduction_pct,
        "summary": (
            f"Choosing {' → '.join(cleanest['path'])} cuts inhaled PM2.5 by "
            f"{reduction_pct}% ({saved_ug} µg saved per one-way trip)."
        ),
    }
