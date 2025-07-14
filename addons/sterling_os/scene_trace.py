from datetime import datetime, timezone
import json
from pathlib import Path

TRACE_FILE = Path(__file__).resolve().parent / "scene_trace.json"


def _load() -> list:
    if TRACE_FILE.exists():
        try:
            return json.loads(TRACE_FILE.read_text())
        except Exception:
            return []
    return []


def record_scene_status(scene_id: str, status: str, agents_involved=None, quorum_score=0.0, interruptible=True, failsafe_triggered=False):
    data = _load()
    entry = {
        "scene": scene_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "agents_involved": agents_involved or [],
        "quorum_score": quorum_score,
        "interruptible": interruptible,
        "failsafe_triggered": failsafe_triggered,
    }
    data.append(entry)
    TRACE_FILE.write_text(json.dumps(data, indent=2))
    return entry

