from __future__ import annotations

"""Simple escalation handling for scene failures and conflicts."""

from datetime import datetime, timezone
from typing import Dict

from . import behavior_audit, scene_status_tracker, memory_manager


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
    # also record in memory timeline for retrospective analysis
    memory_manager.add_event(f"escalation:{scene_id}:{reason}")
    return data


def escalate_to_admin(task: str, error: str, fallback_agent: str) -> Dict:
    """Notify admin of a task failure and fallback switch."""
    message = f"{task} failed: {error}; switched to {fallback_agent}"
    return escalate_scene(task, message)
