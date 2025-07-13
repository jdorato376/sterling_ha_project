from __future__ import annotations

"""Simple escalation handling for scene failures and conflicts."""

from datetime import datetime, timezone
from typing import Dict

from . import behavior_audit, scene_status_tracker


ESCALATION_EVENT = "escalation"


def escalate_scene(scene_id: str, reason: str) -> Dict:
    """Mark a scene as escalated and log the event."""
    timestamp = datetime.now(timezone.utc).isoformat()
    scene_status_tracker.update_status(scene_id, "escalated")
    data = {
        "scene": scene_id,
        "reason": reason,
        "timestamp": timestamp,
    }
    behavior_audit.log_action(ESCALATION_EVENT, data)
    return data
