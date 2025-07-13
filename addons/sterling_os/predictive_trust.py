from __future__ import annotations

"""Rolling trust score computation based on recent events."""

import time
from typing import Dict, List


class PredictiveTrustManager:
    def __init__(self) -> None:
        self.trust_ledger: Dict[str, List[float]] = {}

    def record_success(self, agent: str) -> None:
        now = time.time()
        self.trust_ledger.setdefault(agent, []).append(now)
        self._clean(agent)

    def record_failure(self, agent: str) -> None:
        now = time.time()
        self.trust_ledger.setdefault(agent, []).append(-now)
        self._clean(agent)

    def _clean(self, agent: str) -> None:
        window = 3600
        cutoff = time.time()
        self.trust_ledger[agent] = [t for t in self.trust_ledger[agent] if abs(cutoff - abs(t)) < window]

    def calculate_trust(self, agent: str) -> float:
        events = self.trust_ledger.get(agent, [])
        if not events:
            return 0.5
        positives = sum(1 for t in events if t > 0)
        negatives = sum(1 for t in events if t < 0)
        return round(positives / max(1, positives + negatives), 2)


predictive_trust = PredictiveTrustManager()
