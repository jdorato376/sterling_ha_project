"""Simple trust score registry for agents.

This module stores agent trust weights in ``trust_weights.json``. We expose
helper functions to load, save and modify these weights.  Weight values are
floats between 0 and 1 representing relative confidence in a given agent.
"""

import json
from pathlib import Path
from typing import Dict

TRUST_FILE = Path(__file__).with_name("trust_weights.json")
TRUST_REGISTRY_FILE = Path(__file__).with_name("trust_registry_store.json")

# in-memory registry of current trust weights
trust_registry: Dict[str, float] = {}


def _load_raw_weights() -> Dict[str, dict | float]:
    if TRUST_FILE.exists():
        try:
            return json.loads(TRUST_FILE.read_text())
        except Exception:
            return {}
    return {}


def load_weights() -> Dict[str, float]:
    """Return stored trust weights for agents as a simple mapping."""
    raw = _load_raw_weights()
    result: Dict[str, float] = {}
    for agent_id, entry in raw.items():
        if isinstance(entry, dict):
            result[agent_id] = float(entry.get("trust", 0.0))
        else:
            result[agent_id] = float(entry)
    return result


def save_weights(weights: Dict[str, float], types: Dict[str, str] | None = None) -> None:
    """Persist trust weights to disk, preserving existing agent types."""
    raw = _load_raw_weights()
    for agent_id, weight in weights.items():
        entry = raw.get(agent_id, {}) if isinstance(raw.get(agent_id), dict) else {}
        entry["trust"] = float(weight)
        if types and agent_id in types:
            entry["type"] = types[agent_id]
        raw[agent_id] = entry
    ordered = {k: raw[k] for k in sorted(raw)}
    TRUST_FILE.write_text(json.dumps(ordered, indent=2))


def set_weight(agent_id: str, weight: float) -> float:
    """Persist an exact trust weight for ``agent_id`` and return the value.

    ``weight`` is coerced to ``float`` and clamped between ``0.0`` and ``1.0``.
    This avoids invalid values leaking into the registry.
    """
    weights = load_weights()
    value = float(weight)
    clamped = max(0.0, min(1.0, value))
    weights[agent_id] = clamped
    save_weights(weights)
    trust_registry[agent_id] = clamped
    save_trust_registry()
    return clamped


def update_weight(agent_id: str, delta: float) -> float:
    """Adjust ``agent_id`` weight by ``delta`` and return the new value."""
    weights = load_weights()
    current = float(weights.get(agent_id, 0.0))
    step = float(delta)
    new_weight = max(0.0, min(1.0, current + step))
    weights[agent_id] = new_weight
    save_weights(weights)
    trust_registry[agent_id] = new_weight
    save_trust_registry()
    return new_weight


def save_trust_registry(path: str | Path | None = None) -> None:
    """Persist the in-memory registry to disk."""
    target = Path(path) if path is not None else TRUST_REGISTRY_FILE
    target.write_text(json.dumps(trust_registry, indent=2))


def load_trust_registry(path: str | Path | None = None) -> None:
    """Load the registry from disk if it exists."""
    global trust_registry
    p = Path(path) if path is not None else TRUST_REGISTRY_FILE
    if p.exists():
        try:
            trust_registry = json.loads(p.read_text())
        except Exception:
            trust_registry = {}
    else:
        trust_registry = load_weights()


# initialize registry on import
load_trust_registry()

