from __future__ import annotations

"""Rotate failing agents based on scorecard history."""

import json
import os
from typing import Dict, List

from addons.sterling_os import trust_registry

SCORECARD_FILE = "agent_scorecard.json"
WINDOW = 10
FAIL_THRESHOLD = 3


def _load() -> Dict[str, List[bool]]:
    if os.path.exists(SCORECARD_FILE):
        try:
            return json.loads(open(SCORECARD_FILE).read())
        except Exception:
            return {}
    return {}


def _save(data: Dict[str, List[bool]]) -> None:
    with open(SCORECARD_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_result(agent: str, success: bool) -> None:
    data = _load()
    history = data.get(agent, [])
    history.append(bool(success))
    history = history[-WINDOW:]
    data[agent] = history
    _save(data)


def should_rotate(agent: str) -> bool:
    history = _load().get(agent, [])
    if len(history) < WINDOW:
        return False
    return history.count(False) >= FAIL_THRESHOLD


def rotate_agent(agent: str) -> str | None:
    """Reduce trust weight and return alternate agent id."""
    trust_registry.update_weight(agent, -0.1)
    weights = trust_registry.load_weights()
    alt_candidates = {a: w for a, w in weights.items() if a != agent}
    if not alt_candidates:
        return None
    return max(alt_candidates.items(), key=lambda x: x[1])[0]
