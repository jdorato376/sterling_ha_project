import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from jsonschema import validate, ValidationError

import runtime_memory

MEMORY_PATH = runtime_memory.RUNTIME_STORE.path
SCHEMA_PATH = Path("runtime_memory.schema.json")
SIZE_LIMIT = 10 * 1024 * 1024  # 10MB


def load_schema() -> Dict[str, Any]:
    try:
        with SCHEMA_PATH.open() as f:
            return json.load(f)
    except Exception:
        return {}


def validate_timestamps(data: Dict[str, Any]) -> bool:
    for key in ("agent_trace", "route_logs"):
        for entry in data.get(key, []):
            ts = entry.get("timestamp")
            try:
                datetime.fromisoformat(ts)
            except Exception:
                return False
    return True


def validate_memory() -> bool:
    if not MEMORY_PATH.exists():
        runtime_memory.alert_admin("Memory missing", str(MEMORY_PATH))
        return False

    if MEMORY_PATH.stat().st_size > SIZE_LIMIT:
        runtime_memory.alert_admin("Memory too large", str(MEMORY_PATH.stat().st_size))
        return False

    try:
        with MEMORY_PATH.open() as f:
            data = json.load(f)
    except Exception as exc:
        runtime_memory.alert_admin("Memory corrupt", str(exc))
        return False

    schema = load_schema()
    if schema:
        try:
            validate(instance=data, schema=schema)
        except ValidationError as exc:
            runtime_memory.alert_admin("Schema mismatch", str(exc))
            return False

    if not validate_timestamps(data):
        runtime_memory.alert_admin("Invalid timestamp", "format error")
        return False

    return True


def backup_and_reset() -> None:
    idx = 1
    while MEMORY_PATH.with_suffix(f".bak.{idx}").exists():
        idx += 1
    backup = MEMORY_PATH.with_suffix(f".bak.{idx}")
    try:
        if MEMORY_PATH.exists():
            MEMORY_PATH.rename(backup)
    except Exception:
        pass
    runtime_memory.RUNTIME_STORE.write(runtime_memory.RUNTIME_STORE.default)


def main() -> None:
    if not validate_memory():
        backup_and_reset()
        print("Runtime memory invalid - reset performed")
    else:
        print("Runtime memory is valid")


if __name__ == "__main__":
    main()
