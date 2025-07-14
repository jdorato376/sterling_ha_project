from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any


def log_memory_entry(query: str, response: str, persona_context: str = "general") -> None:
    """Append a summarized memory entry for the given persona."""
    memory_dir = Path("addons/sterling_os/memory")
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_path = memory_dir / f"{persona_context}_memory.json"
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "topic": query[:50],
        "summary": response[:200],
    }
    memory = []
    if memory_path.exists():
        try:
            with open(memory_path, "r") as f:
                memory = json.load(f)
        except Exception:
            memory = []
    memory.append(entry)
    with open(memory_path, "w") as f:
        json.dump(memory[-100:], f, indent=2)
