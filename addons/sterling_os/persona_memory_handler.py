"""Isolate personal and professional memory contexts."""
from __future__ import annotations

from typing import Any, Dict


class PersonaMemoryHandler:
    """Simple in-memory context separation."""

    def __init__(self) -> None:
        self._personal: Dict[str, Any] = {}
        self._professional: Dict[str, Any] = {}

    def store(self, persona: str, key: str, value: Any) -> None:
        if persona == "personal":
            self._personal[key] = value
        else:
            self._professional[key] = value

    def retrieve(self, persona: str, key: str) -> Any:
        if persona == "personal":
            return self._personal.get(key)
        return self._professional.get(key)
