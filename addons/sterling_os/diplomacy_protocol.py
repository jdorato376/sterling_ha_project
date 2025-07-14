from __future__ import annotations

"""Basic conflict mediation between agents."""

from typing import Dict, Optional


def mediate(votes: Dict[str, bool], trust: Dict[str, float]) -> Optional[bool]:
    """Return consensus result or ``None`` if tied."""
    approve = sum(trust.get(a, 0.0) for a, v in votes.items() if v)
    reject = sum(trust.get(a, 0.0) for a, v in votes.items() if not v)
    if approve > reject:
        return True
    if reject > approve:
        return False
    return None


def propose_rebalance(votes: Dict[str, bool], trust: Dict[str, float]) -> Dict[str, float]:
    """Suggest trust rebalancing after a vote."""
    updated = {}
    for agent, vote in votes.items():
        delta = 0.05 if vote else -0.05
        updated[agent] = max(0.0, min(1.0, trust.get(agent, 0.0) + delta))
    return updated
