"""Thread lock management for sovereign scenes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "thread_registry.json"


def _load() -> Dict[str, Dict]:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(data: Dict[str, Dict]) -> None:
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))


def lock_thread(name: str) -> bool:
    data = _load()
    if name in data:
        data[name]["locked"] = True
        _save(data)
        return True
    return False


def unlock_thread(name: str) -> bool:
    data = _load()
    if name in data:
        data[name]["locked"] = False
        _save(data)
        return True
    return False


def is_locked(name: str) -> bool:
    data = _load()
    return bool(data.get(name, {}).get("locked"))

__all__ = ["lock_thread", "unlock_thread", "is_locked", "REGISTRY_FILE"]
