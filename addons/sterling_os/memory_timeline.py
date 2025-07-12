from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

from json_store import JSONStore

STORE = JSONStore(Path(__file__).resolve().parent / "memory_timeline.json", default=[])


def load_timeline() -> List[Dict]:
    """Return stored timeline entries."""
    return STORE.read()


def log_event(action: str, result: str, initiator: str) -> Dict:
    """Append a structured event to the timeline."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "result": result,
        "initiator": initiator,
    }
    data = load_timeline()
    data.append(entry)
    STORE.write(data)
    return entry
