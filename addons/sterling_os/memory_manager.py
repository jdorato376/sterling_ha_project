"""Simple JSON-based memory timeline manager."""

from collections import OrderedDict
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict

from json_store import JSONStore

MEMORY_STORE = JSONStore(Path(__file__).resolve().parent / "memory_timeline.json", default=[])


@dataclass(slots=True)
class TimelineEvent:
    """Structured timeline entry."""

    timestamp: str
    event: str

# Keep a small LRU cache of recently logged phrases to reduce disk writes
RECENT_CACHE_SIZE = 20
_RECENT_PHRASE_CACHE: OrderedDict[str, datetime] = OrderedDict()


def load_memory() -> List[Dict]:
    """Return the parsed timeline data."""
    return MEMORY_STORE.read()


def add_event(event: str) -> None:
    """Append a timestamped event string to the timeline."""
    data = load_memory()
    data.append(
        asdict(
            TimelineEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event=event,
            )
        )
    )
    MEMORY_STORE.write(data)


def log_phrase(query: str, intent: Optional[str] = None) -> None:
    """Log a spoken phrase and optional resolved intent."""
    if query in _RECENT_PHRASE_CACHE:
        _RECENT_PHRASE_CACHE.move_to_end(query)
        return

    _RECENT_PHRASE_CACHE[query] = datetime.now(timezone.utc)
    if len(_RECENT_PHRASE_CACHE) > RECENT_CACHE_SIZE:
        _RECENT_PHRASE_CACHE.popitem(last=False)

    if intent:
        add_event(f"phrase:{query}|intent:{intent}")
    else:
        add_event(f"phrase:{query}")


def reset_memory() -> list:
    """Clear the timeline file and return an empty list."""
    MEMORY_STORE.write([])
    _RECENT_PHRASE_CACHE.clear()
    return []


def get_timeline(
    limit: Optional[int] = None,
    tag: Optional[str] = None,
    tags: Optional[List[str]] = None,
    event_type: Optional[str] = None,
    since: Optional[datetime] = None,
    contains: Optional[str] = None,
) -> List[Dict]:
    """Return timeline events filtered by various parameters."""
    data = load_memory()
    if since:
        data = [e for e in data if datetime.fromisoformat(e["timestamp"]) >= since]
    if tag:
        data = [evt for evt in data if evt.get("event", "").startswith(f"{tag}:")]
    if tags:
        data = [evt for evt in data if any(evt.get("event", "").startswith(f"{t}:") for t in tags)]
    if event_type:
        data = [evt for evt in data if evt.get("event", "").split(":", 1)[0] == event_type]
    if contains:
        data = [evt for evt in data if contains.lower() in evt.get("event", "").lower()]
    if limit is not None:
        data = data[-limit:]
    return data


def get_recent_phrases(limit: int = 5, contains: Optional[str] = None) -> List[Dict]:
    """Return recent phrase log entries."""
    return get_timeline(limit=limit, tag="phrase", contains=contains)
