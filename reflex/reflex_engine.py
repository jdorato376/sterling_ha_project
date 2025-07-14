"""Emergency reflex engine for scene rollback and escalation."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict
from pathlib import Path
import json
import types

try:
    from addons.sterling_os import escalation_engine
except Exception:  # pragma: no cover - standalone execution
    escalation_engine = types.SimpleNamespace(escalate_scene=lambda scene, reason: {
        'scene': scene,
        'reason': reason,
        'status': 'escalated',
    })

SHIELD_FILE = Path(__file__).resolve().parent / 'autonomy_shield.yaml'
PROTOCOL_FILE = Path(__file__).resolve().parent / 'emergency_protocols.json'


def load_shield() -> Dict:
    if SHIELD_FILE.exists():
        import yaml
        return yaml.safe_load(SHIELD_FILE.read_text()) or {}
    return {}


def load_protocols() -> Dict:
    if PROTOCOL_FILE.exists():
        return json.loads(PROTOCOL_FILE.read_text())
    return {}


def monitor_event(scene: str, duration: int, trust_score: float) -> Dict:
    """Monitor events and trigger escalation if thresholds exceeded."""
    shield = load_shield().get('protection', {})
    triggers = shield.get('triggers', [])
    if duration > 90 or trust_score < 60 or 'agent_missing_heartbeat' in triggers:
        reason = f"duration={duration};trust={trust_score}"
        return escalation_engine.escalate_scene(scene, reason)
    return {
        'scene': scene,
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
