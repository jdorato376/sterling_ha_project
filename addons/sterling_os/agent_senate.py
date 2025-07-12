"""Simplified multi-agent voting mechanism."""

from typing import Iterable, Dict


class AgentSenate:
    def __init__(self, agents: Iterable[str]):
        self.agents = list(agents)

    def decide(self, votes: Dict[str, bool], quorum: int | None = None) -> bool:
        """Return True if approvals meet the quorum."""
        quorum = quorum or (len(self.agents) // 2 + 1)
        approvals = sum(1 for agent, approve in votes.items() if approve)
        return approvals >= quorum
