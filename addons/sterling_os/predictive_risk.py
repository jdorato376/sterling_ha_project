from __future__ import annotations

"""Flag potential risks based on trust and anomalies."""

from typing import List, Dict

from addons.sterling_os import trust_registry
from addons.sterling_os import codex_diagnostics


def evaluate_risk(weights: Dict[str, float], scene_anomalies: int, intent_mismatches: int) -> List[str]:
    risks: List[str] = []
    for agent, weight in weights.items():
        if weight < 0.3:
            risks.append(f"low_weight:{agent}")
    if scene_anomalies > 5:
        risks.append("high_scene_anomalies")
    if intent_mismatches > 5:
        risks.append("high_intent_mismatches")
    if risks:
        codex_diagnostics.log_risk(risks)
    return risks
