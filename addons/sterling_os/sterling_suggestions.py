from __future__ import annotations

"""Generate proactive suggestions based on timeline or delta logs."""

from typing import List, Dict


def suggest_from_deltas(deltas: List[Dict]) -> List[str]:
    """Return simple suggestion strings for each delta entry."""
    suggestions: List[str] = []
    for entry in deltas:
        for key, info in entry.items():
            suggestions.append(
                f"Adjust {key} from {info.get('current')} to {info.get('expected')}?"
            )
    return suggestions
