from __future__ import annotations

"""Simple diagnostics logger."""

import json
import os
from datetime import datetime, timezone
from typing import List

DIAG_LOG = "diagnostics_log.json"


def _load() -> List[dict]:
    if os.path.exists(DIAG_LOG):
        try:
            return json.loads(open(DIAG_LOG).read())
        except Exception:
            return []
    return []


def _save(data: List[dict]) -> None:
    with open(DIAG_LOG, "w") as f:
        json.dump(data, f, indent=2)


def log_risk(risks: List[str]) -> None:
    log = _load()
    log.append({"timestamp": datetime.now(timezone.utc).isoformat(), "risks": risks})
    _save(log)
