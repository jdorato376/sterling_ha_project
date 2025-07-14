from __future__ import annotations

"""Simple constitution layer for agent governance."""

import json
from pathlib import Path
from typing import Dict, List

CONSTITUTION_FILE = Path(__file__).with_name("phase11_codex_constitution.json")


def _load() -> Dict[str, dict]:
    """Return the raw constitution mapping."""
    if CONSTITUTION_FILE.exists():
        try:
            return json.loads(CONSTITUTION_FILE.read_text())
        except Exception:
            return {}
    return {}


def get_rules(agent: str) -> Dict:
    data = _load()
    agents = data.get("agents", data)
    return agents.get(agent, {})


def get_protocols() -> Dict:
    data = _load()
    return data.get("escalation_protocols", {})


def can_act(agent: str, action: str) -> bool:
    rules = get_rules(agent)
    allowed: List[str] = rules.get("allowed", [])
    return action in allowed or "*" in allowed


def requires_escalation(agent: str, action: str) -> bool:
    rules = get_rules(agent)
    escalate: List[str] = rules.get("escalate", [])
    return action in escalate


def can_override(agent: str, target: str) -> bool:
    rules = get_rules(agent)
    if target in rules.get("cannot_override", []):
        return False
    if target in rules.get("can_override", []):
        return True
    return False

