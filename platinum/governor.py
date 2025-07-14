from __future__ import annotations

"""Platinum Dominion governance core."""

import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime, timezone

import yaml

BASE_DIR = Path(__file__).resolve().parent
TRUST_FILE = BASE_DIR / "trust_scores.json"
MATRIX_FILE = BASE_DIR / "diplomacy_matrix.json"
LOGBOOK_FILE = BASE_DIR / "governance_logbook.yaml"
DIRECTIVES_FILE = BASE_DIR / "governance_directives.yaml"


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2))


def _append_yaml(path: Path, item: Dict) -> None:
    existing = []
    if path.exists():
        try:
            loaded = yaml.safe_load(path.read_text())
            if isinstance(loaded, list):
                existing = loaded
        except Exception:
            existing = []
    existing.append(item)
    path.write_text(yaml.safe_dump(existing))


class PlatinumGovernor:
    """Manage trust scores and logbook entries."""

    def __init__(self) -> None:
        self.trust: Dict[str, float] = _load_json(TRUST_FILE, {})
        self.directives = _load_json(DIRECTIVES_FILE, {})

    def check(self, agent: str, threshold: float) -> bool:
        score = float(self.trust.get(agent, 0.0))
        return score >= threshold

    def log_action(self, action: str, data: Dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
        }
        record.update(data)
        _append_yaml(LOGBOOK_FILE, record)

    def update_trust(self, agent: str, delta: float) -> float:
        score = float(self.trust.get(agent, 0.0))
        score = max(0.0, min(1.0, score + float(delta)))
        self.trust[agent] = score
        _save_json(TRUST_FILE, self.trust)
        return score


GOVERNOR = PlatinumGovernor()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Platinum Governor utility")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--agent")
    parser.add_argument("--score-threshold", type=float, default=0.0)
    args = parser.parse_args()

    if args.check and args.agent:
        ok = GOVERNOR.check(args.agent, args.score_threshold)
        sys.exit(0 if ok else 1)
