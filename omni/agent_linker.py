from __future__ import annotations

"""Simple registry for active agents and their capabilities."""

import json
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
LEDGER_FILE = BASE_DIR / "agent_registry.json"


def _load() -> Dict[str, Dict]:
    if LEDGER_FILE.exists():
        try:
            return json.loads(LEDGER_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(data: Dict[str, Dict]) -> None:
    LEDGER_FILE.write_text(json.dumps(data, indent=2))


def register_agent(name: str, capabilities: List[str]) -> Dict[str, Dict]:
    """Register an agent with capabilities."""
    data = _load()
    data[name] = {
        "capabilities": capabilities,
        "heartbeat": False,
        "escalation_ready": False,
    }
    _save(data)
    return data[name]


def update_heartbeat(name: str, status: bool = True) -> bool:
    """Update heartbeat flag for agent."""
    data = _load()
    if name in data:
        data[name]["heartbeat"] = status
        _save(data)
        return True
    return False

__all__ = ["register_agent", "update_heartbeat", "LEDGER_FILE"]
