from __future__ import annotations

"""Simple escalation handling for scene failures and conflicts."""

from datetime import datetime, timezone
from typing import Dict

try:
    from . import behavior_audit, scene_status_tracker, memory_manager
    from . import agent_constitution
except Exception:  # pragma: no cover - allow standalone execution
    import importlib.util
    from pathlib import Path
    _base = Path(__file__).resolve().parent
    for name in ["behavior_audit", "scene_status_tracker", "memory_manager", "agent_constitution"]:
        spec = importlib.util.spec_from_file_location(name, _base / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        globals()[name] = mod
try:  # optional governor integration
    from platinum import GOVERNOR
except Exception:  # pragma: no cover - governor optional
    GOVERNOR = None


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
    if GOVERNOR is not None:
        try:
            GOVERNOR.log_action(ESCALATION_EVENT, data)
        except Exception:
            pass  # pragma: no cover
    return data


def escalate_to_admin(task: str, error: str, fallback_agent: str) -> Dict:
    """Notify admin of a task failure and fallback switch."""
    message = f"{task} failed: {error}; switched to {fallback_agent}"
    return escalate_scene(task, message)


def should_escalate(scene_confidence: float, agent_weight: float) -> bool:
    """Return True if uncertainty or low trust warrants escalation."""
    protocols = agent_constitution.get_protocols()
    threshold = float(protocols.get("uncertainty_threshold", 0.2))
    return scene_confidence < threshold or agent_weight < 0.5

