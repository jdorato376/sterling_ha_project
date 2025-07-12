from __future__ import annotations

"""Runtime memory management with schema validation and health checks."""

import json
import logging
from pathlib import Path
from typing import Dict

from jsonschema import validate, ValidationError

from json_store import JSONStore

logger = logging.getLogger(__name__)

RUNTIME_MEMORY_PATH = Path("runtime_memory.json")
SCHEMA_PATH = Path("runtime_memory.schema.json")

RUNTIME_STORE = JSONStore(RUNTIME_MEMORY_PATH, default={})


def _load_schema() -> Dict:
    try:
        with SCHEMA_PATH.open() as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover - log error only
        logger.error("Failed to load memory schema: %s", exc)
        return {}


def validate_memory_schema(memory_data: Dict) -> bool:
    schema = _load_schema()
    if not schema:
        return True
    try:
        validate(instance=memory_data, schema=schema)
        return True
    except ValidationError as e:
        logger.error("Memory schema validation failed: %s", e)
        return False


def _backup_invalid(data: Dict) -> None:
    backup = RUNTIME_STORE.path.with_suffix(".bak")
    try:
        with backup.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:  # pragma: no cover - best effort
        pass


def read_memory() -> Dict:
    data = RUNTIME_STORE.read()
    if validate_memory_schema(data):
        return data
    _backup_invalid(data)
    RUNTIME_STORE.write(RUNTIME_STORE.default)
    return RUNTIME_STORE.default.copy()


def write_memory(data: Dict) -> None:
    if validate_memory_schema(data):
        RUNTIME_STORE.write(data)
    else:
        _backup_invalid(data)
        # refuse to overwrite with invalid data


def alert_admin(message: str, detail: str) -> None:  # pragma: no cover - thin wrapper
    """Log an alert message for administrative visibility."""
    logger.error("%s: %s", message, detail)


def run_health_check() -> None:
    """Validate that the runtime memory file exists and conforms to the schema."""
    if not RUNTIME_STORE.path.exists():
        raise RuntimeError("Missing memory file")
    try:
        with RUNTIME_STORE.path.open() as f:
            data = json.load(f)
    except Exception as exc:
        alert_admin("Memory check failed", str(exc))
        raise RuntimeError("Invalid runtime memory") from exc
    if not validate_memory_schema(data):
        alert_admin("Memory schema invalid", "validation error")
        raise RuntimeError("Invalid runtime memory schema")


__all__ = [
    "RUNTIME_STORE",
    "read_memory",
    "write_memory",
    "run_health_check",
    "alert_admin",
]


