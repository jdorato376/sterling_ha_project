from __future__ import annotations

"""Write immutable audit logs for scene behavior."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

AUDIT_FILE = Path(__file__).resolve().parents[2] / "audits" / "scene_audit.jsonl"
HASH_FILE = AUDIT_FILE.with_suffix(".sha256")


def _update_hash() -> None:
    digest = hashlib.sha256(AUDIT_FILE.read_bytes() if AUDIT_FILE.exists() else b"").hexdigest()
    HASH_FILE.write_text(digest)


def verify_hash() -> bool:
    if not AUDIT_FILE.exists() or not HASH_FILE.exists():
        return False
    current = hashlib.sha256(AUDIT_FILE.read_bytes()).hexdigest()
    saved = HASH_FILE.read_text().strip()
    return current == saved


def log_action(action: str, data: Dict) -> None:
    """Append an audit entry and update integrity hash."""
    AUDIT_FILE.parent.mkdir(exist_ok=True)
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "action": action}
    entry.update(data)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    _update_hash()
