from __future__ import annotations

"""Track differences between current and expected automation scenes."""

from pathlib import Path
import json
import yaml
from typing import Dict

CURRENT_STATE_FILE = Path(__file__).resolve().parent / "current_scene_state.json"
EXPECTED_MODEL_FILE = Path(__file__).resolve().parent / "expected_behavior_model.json"
DELTA_LOG_FILE = Path(__file__).resolve().parent / "delta_log.yaml"


def _load_json(path: Path) -> Dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def compute_delta(current: Dict, expected: Dict) -> Dict:
    """Return a dict describing mismatches between states."""
    delta: Dict[str, Dict[str, object]] = {}
    for key, value in expected.items():
        if current.get(key) != value:
            delta[key] = {"current": current.get(key), "expected": value}
    return delta


def update_delta() -> Dict:
    """Load state files, compute delta and append to log."""
    current = _load_json(CURRENT_STATE_FILE)
    expected = _load_json(EXPECTED_MODEL_FILE)
    delta = compute_delta(current, expected)
    if delta:
        log = []
        if DELTA_LOG_FILE.exists():
            log = yaml.safe_load(DELTA_LOG_FILE.read_text()) or []
        log.append(delta)
        DELTA_LOG_FILE.write_text(yaml.safe_dump(log, sort_keys=False))
    return delta
