from __future__ import annotations
"""Simple Magistrate agent for scene reasoning review."""

import json
from pathlib import Path
from typing import Dict

SCENE_LOG = Path(__file__).resolve().parent / "scene_reason_log.json"
VERDICT_LEDGER = Path(__file__).resolve().parent / "verdict_ledger.yaml"

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def review_scene(scene_id: str) -> Dict:
    """Return reasoning for a scene and record verdict."""
    log_entries = []
    if SCENE_LOG.exists():
        try:
            log_entries = json.loads(SCENE_LOG.read_text())
            if not isinstance(log_entries, list):
                log_entries = [log_entries]
        except Exception:
            log_entries = []
    scene = next((s for s in log_entries if s.get("scene_id") == scene_id), None)
    verdict = {
        "scene_id": scene_id,
        "ruling": "UPHELD" if scene else "NOT_FOUND",
    }
    if yaml:
        existing = []
        if VERDICT_LEDGER.exists():
            try:
                existing = yaml.safe_load(VERDICT_LEDGER.read_text()) or []
            except Exception:
                existing = []
        existing.append(verdict)
        VERDICT_LEDGER.write_text(yaml.safe_dump(existing))
    return verdict

__all__ = ["review_scene"]
