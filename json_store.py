from __future__ import annotations

"""Utility helpers for simple JSON file persistence."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import json


@dataclass(slots=True)
class JSONStore:
    """Lightweight JSON file store wrapper."""

    path: Path
    default: Dict[str, Any] = field(default_factory=dict)

    def read(self) -> Dict[str, Any]:
        """Load JSON data from ``path`` or return ``default`` if invalid."""
        if self.path.exists():
            try:
                with self.path.open() as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.default.copy()
        return self.default.copy()

    def write(self, data: Dict[str, Any]) -> None:
        """Write JSON data to ``path`` with indentation."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            json.dump(data, f, indent=2)
