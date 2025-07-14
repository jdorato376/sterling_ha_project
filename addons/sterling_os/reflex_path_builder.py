"""Generate reflex command execution paths."""
from __future__ import annotations

from typing import Dict, List


def build_path(intent: str, state: Dict[str, str] | None = None) -> List[str]:
    """Return the command path for a given intent."""
    path = [intent]
    if state and state.get("fallback"):
        path.append("fallback")
    return path
