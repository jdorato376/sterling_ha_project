"""Scene trace utilities for resilience testing and self-healing logic."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from addons.sterling_os.audit_logger import log_event

# Default trace file path (tests may monkeypatch this)
TRACE_FILE = Path(__file__).resolve().parent / "scene_trace.json"


def record_scene_status(
    scene: str,
    status: str,
    agents: list[str] | None = None,
    quorum_score: float | None = None,
) -> dict:
    """Record a scene execution entry and persist it to ``TRACE_FILE``."""

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "scene": scene,
        "status": status,
        "agents": agents or [],
    }
    if quorum_score is not None:
        entry["quorum_score"] = quorum_score

    os.makedirs(os.path.dirname(TRACE_FILE), exist_ok=True)

    if os.path.exists(TRACE_FILE):
        try:
            with open(TRACE_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []

    if isinstance(data, dict) and "executions" in data:
        data = data.get("executions", [])

    data.append(entry)
    with open(TRACE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    log_event("scene_trace", status)
    return entry


def trace_scene(scene_id: str, status: str, notes=None) -> None:
    """Legacy wrapper preserved for backward compatibility."""
    record_scene_status(scene_id, status, notes or [])


if __name__ == "__main__":
    trace_scene("startup_check", "success", {"boot_phase": "21"})
