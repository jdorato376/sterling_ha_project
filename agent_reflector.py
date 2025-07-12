"""Reflective agent execution and logging layer."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Dict, Tuple

import schema_escalator
import runtime_memory

# Alias for backwards compatibility
RUNTIME_STORE = runtime_memory.RUNTIME_STORE


def reflect(agent: str, query: str, result: Dict, fallback_handler: Callable[[str], Dict]) -> Tuple[Dict, bool, bool]:
    """Log agent result and escalate if schema check fails."""
    success = schema_escalator.check_schema(agent, result)
    data = runtime_memory.read_memory()
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
    runtime_memory.write_memory(data)
    return result, success, fallback

__all__ = ["reflect"]
