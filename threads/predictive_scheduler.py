"""Predictive scheduler for thread reprioritization."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "thread_registry.json"


def load_registry() -> Dict[str, Dict]:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text())
        except Exception:
            return {}
    return {}


def reprioritize() -> List[str]:
    data = load_registry()
    # simple sort by locked status then last executed (older first)
    threads = list(data.items())
    threads.sort(key=lambda item: (item[1].get("locked", False), item[1].get("last_executed", "")))
    return [name for name, _ in threads]

__all__ = ["load_registry", "reprioritize", "REGISTRY_FILE"]
