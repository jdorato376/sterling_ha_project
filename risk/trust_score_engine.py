"""Simple engine calculating agent trust scores."""
from __future__ import annotations

from typing import Dict


def compute_score(metrics: Dict[str, float]) -> float:
    """Compute a trust score out of 100 from metric weights."""
    asr = metrics.get('success_rate', 1.0) * 100
    ef = metrics.get('escalation_frequency', 0.0) * 10
    oc = metrics.get('override_count', 0.0) * 5
    fsi = metrics.get('failure_severity', 0.0) * 2
    score = asr - ef - oc - fsi
    if score < 0:
        return 0.0
    if score > 100:
        return 100.0
    return round(score, 1)
