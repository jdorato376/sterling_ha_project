from __future__ import annotations
"""Internal Ethics Engine for arbitration decisions."""

import json
from pathlib import Path
from typing import Dict

import yaml

BASE_DIR = Path(__file__).resolve().parent
CONSTITUTION_FILE = BASE_DIR / "sterling_constitution.yaml"
PRECEDENT_FILE = BASE_DIR / "ethical_precedent_ledger.json"


def _load_yaml(path: Path) -> Dict:
    if path.exists():
        try:
            return yaml.safe_load(path.read_text()) or {}
        except Exception:
            return {}
    return {}


def _load_json(path: Path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def _save_json(path: Path, data: Dict) -> None:
    path.write_text(json.dumps(data, indent=2))


class EthicsEngine:
    """Evaluate agent proposals against the Sterling Constitution."""

    def __init__(self) -> None:
        self.constitution = _load_yaml(CONSTITUTION_FILE)
        self.precedent = _load_json(PRECEDENT_FILE)

    def evaluate(self, command: str, proposals: Dict[str, str], trust: Dict[str, float], risk: str) -> Dict:
        """Return the approved agent and log the decision."""
        hierarchy = self.constitution.get("hierarchy", {})
        best_agent = None
        best_score = -1.0
        for agent in proposals:
            weight = hierarchy.get(agent, 50) / 100
            score = trust.get(agent, 0.0) * weight
            if score > best_score:
                best_agent = agent
                best_score = score
        result = {
            "command": command,
            "approved_agent": best_agent,
            "risk": risk,
        }
        self.precedent[command] = result
        _save_json(PRECEDENT_FILE, self.precedent)
        return result


ENGINE = EthicsEngine()
