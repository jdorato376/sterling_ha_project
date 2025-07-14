"""Simple mutation engine."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "agent_dna_registry.json"


def load_registry() -> Dict[str, Any]:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text())
        except Exception:
            return {}
    return {}


def mutate_agent(agent: str, new_role: str) -> None:
    data = load_registry()
    info = data.get(agent, {})
    info.setdefault("roles", [])
    if new_role not in info["roles"]:
        info["roles"].append(new_role)
    info["last_mutation"] = datetime.now(timezone.utc).isoformat()
    data[agent] = info
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))

__all__ = ["load_registry", "mutate_agent"]
