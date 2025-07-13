from __future__ import annotations

"""Predict imminent infrastructure failures."""

import json
import os
from datetime import datetime, timezone
from typing import Dict

REPAIR_LOG = "infra_resets.json"


def _load_log() -> list:
    if os.path.exists(REPAIR_LOG):
        try:
            return json.loads(open(REPAIR_LOG).read())
        except Exception:
            return []
    return []


def _save_log(data: list) -> None:
    with open(REPAIR_LOG, "w") as f:
        json.dump(data, f, indent=2)


def analyze_metrics(cpu: float, mem: float, load: float, net_err: float, threshold: float = 0.8) -> float:
    """Return confidence score that repair is needed."""
    values = [cpu, mem, load, net_err]
    score = sum(1 for v in values if v > threshold) / len(values)
    return round(score, 2)


def predictive_repair(cpu: float, mem: float, load: float, net_err: float) -> Dict:
    """Return suggestion dict if confidence exceeds 0.75."""
    confidence = analyze_metrics(cpu, mem, load, net_err)
    if confidence > 0.75:
        log = _load_log()
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": cpu,
            "mem": mem,
            "load": load,
            "net_err": net_err,
        })
        _save_log(log)
        return {"action": "repair", "confidence": confidence}
    return {"action": "ok", "confidence": confidence}
