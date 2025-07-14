from __future__ import annotations

"""Placeholder engine for self-writing automations."""

from typing import List
import yaml


def infer_automation(events: List[str]) -> str:
    """Return a YAML snippet representing an inferred automation."""
    if any("motion" in e for e in events):
        data = {
            "alias": "Auto motion lights",
            "trigger": [{"platform": "event", "event_type": "motion_detected"}],
            "action": [
                {
                    "service": "light.turn_on",
                    "target": {"entity_id": "light.hallway"},
                }
            ],
        }
    else:
        data = {
            "alias": "Generic automation",
            "trigger": [{"platform": "time", "at": "00:00:00"}],
            "action": [{"service": "persistent_notification.create", "data": {"message": "Automation fired"}}],
        }
    return yaml.safe_dump({"automation": [data]}, sort_keys=False)
