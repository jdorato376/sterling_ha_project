"""Reflective agent execution and logging layer."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Tuple

from json_store import JSONStore

import schema_escalator

RUNTIME_STORE = JSONStore(Path("runtime_memory.json"))


def reflect(agent: str, query: str, result: Dict, fallback_handler: Callable[[str], Dict]) -> Tuple[Dict, bool, bool]:
    """Log agent result and escalate if schema check fails."""
    success = schema_escalator.check_schema(agent, result)
    data = RUNTIME_STORE.read()
    trace = data.setdefault("agent_trace", [])
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "query": query,
        "success": success,
    }
    fallback = False
    if not success:
        fallback = True
        data["fallback_triggered"] = True
        path = data.setdefault("escalation_path", [])
        path.append(agent)
        result = fallback_handler(query)
        entry["escalated_to"] = "general"
    else:
        data["fallback_triggered"] = False
    data["last_success"] = bool(success)
    trace.append(entry)
    RUNTIME_STORE.write(data)
    return result, success, fallback

__all__ = ["reflect"]
