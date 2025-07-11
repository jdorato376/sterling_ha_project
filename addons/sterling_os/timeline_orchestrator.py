import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from . import memory_manager


def build_timeline() -> List[Dict]:
    """Return events sorted chronologically."""
    events = memory_manager.load_memory()
    return sorted(events, key=lambda e: e.get("timestamp", ""))


def prune_older_than(days: int) -> List[Dict]:
    """Remove events older than the given number of days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    events = memory_manager.load_memory()
    remaining = [
        e for e in events if datetime.fromisoformat(e["timestamp"]) >= cutoff
    ]
    with memory_manager.MEMORY_FILE.open("w") as f:
        json.dump(remaining, f, indent=2)
    return remaining


def timeline_summary(limit: int = 5) -> str:
    """Return a short natural language summary of recent events."""
    events = build_timeline()[-limit:]
    parts = [f"{e['event']} at {e['timestamp']}" for e in events]
    return "; ".join(parts)
