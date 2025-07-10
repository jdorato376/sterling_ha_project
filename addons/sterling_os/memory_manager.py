"""Simple JSON-based memory timeline manager."""

import json
from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path(__file__).resolve().parent / "memory_timeline.json"


def load_memory():
    """Return the parsed timeline data."""
    if MEMORY_FILE.exists():
        with MEMORY_FILE.open() as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def add_event(event: str):
    """Append a timestamped event to the timeline."""
    data = load_memory()
    data.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
    })
    with MEMORY_FILE.open("w") as f:
        json.dump(data, f)


def reset_memory():
    """Clear the timeline file and return an empty list."""
    with MEMORY_FILE.open("w") as f:
        json.dump([], f)
    return []


def get_timeline():
    """Alias for load_memory for external modules."""
    return load_memory()
