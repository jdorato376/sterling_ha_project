from __future__ import annotations

"""Translate simple natural language descriptions into YAML scene definitions."""

import yaml
from typing import Dict


def compose(description: str) -> str:
    """Return a YAML scene from a naive heuristic parser."""
    desc_lower = description.lower()
    scene: Dict[str, object] = {"alias": "Generated Scene", "trigger": [], "condition": [], "action": []}

    if "9 pm" in desc_lower or "21" in desc_lower:
        scene["condition"].append({"condition": "time", "after": "21:00:00"})

    if "lights" in desc_lower:
        scene["action"].append({"service": "scene.turn_on", "target": {"entity_id": "scene.night_mode"}})

    return yaml.safe_dump(scene, sort_keys=False)
