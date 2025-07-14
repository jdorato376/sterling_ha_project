"""Lightweight intent prediction engine for Sterling OS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class IntentOracle:
    """Predict user intent from queries and context."""

    history: List[str] = field(default_factory=list)

    def predict(self, query: str, context: Dict[str, Any] | None = None) -> str:
        """Return a best-effort intent label."""
        text = query.lower()
        self.history.append(text)
        if "briefing" in text:
            return "daily_briefing"
        if "scene" in text:
            return "launch_scene"
        return "general"


ORACLE = IntentOracle()
