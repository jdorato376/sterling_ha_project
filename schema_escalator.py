"""Schema-driven escalation checks for agent responses."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from json_store import JSONStore

SCHEMA_STORE = JSONStore(Path("runtime_schema.json"))


def _load_schema() -> Dict:
    return SCHEMA_STORE.read()


def check_schema(agent: str, result: Dict) -> bool:
    """Return True if the result meets schema expectations."""
    schema = _load_schema().get(agent)
    if not schema:
        return True
    expected = schema.get("expected_keys", [])
    for key in expected:
        if key not in result:
            return False
    success_value = schema.get("success_value")
    if success_value is not None and expected:
        if result.get(expected[0]) != success_value:
            return False
    return True

__all__ = ["check_schema"]
