from __future__ import annotations

"""Monitor API endpoint health and disable flaky ones."""

from typing import Dict, List

API_HEALTH: Dict[str, Dict[str, List[float] | int | bool]] = {}


def record_call(endpoint: str, latency: float, success: bool = True) -> None:
    data = API_HEALTH.setdefault(endpoint, {"lat": [], "fail": 0, "disabled": False})
    data["lat"].append(latency)
    data["lat"] = data["lat"][-5:]
    if success:
        data["fail"] = 0
    else:
        data["fail"] += 1
    if data["fail"] >= 3 or (len(data["lat"]) >= 5 and sum(data["lat"]) / len(data["lat"]) > 2.0):
        data["disabled"] = True


def is_disabled(endpoint: str) -> bool:
    return API_HEALTH.get(endpoint, {}).get("disabled", False)
