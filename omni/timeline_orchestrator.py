from __future__ import annotations

"""Simple timeline fusion utility."""

from typing import List, Dict


def fuse_timelines(*timelines: List[Dict]) -> List[Dict]:
    """Merge multiple lists of tasks by timestamp."""
    merged: List[Dict] = []
    for timeline in timelines:
        if isinstance(timeline, list):
            merged.extend(timeline)
    return sorted(merged, key=lambda t: t.get("timestamp", 0))

__all__ = ["fuse_timelines"]
