"""Simplified multi-agent voting mechanism."""

from typing import Iterable, Dict, List

from . import trust_registry, escalation_engine, diplomacy_protocol


class AgentSenate:
    def __init__(self, agents: Iterable[str]):
        self.agents = list(agents)

    def decide(self, votes: Dict[str, bool], quorum: int | None = None) -> bool:
        """Return True if approvals meet the quorum, escalate on ties."""
        quorum = quorum or (len(self.agents) // 2 + 1)
        approvals = sum(1 for _, approve in votes.items() if approve)
        rejections = len(votes) - approvals

        if approvals == rejections:
            result = diplomacy_protocol.mediate(votes, trust_registry.load_weights())
            if result is None:
                escalation_engine.escalate_scene("agent_vote", "tie")
                return False
            return result

        return approvals >= quorum

    def vote_on_action(self, agent_responses: List[Dict]) -> Dict:
        """Return the highest weighted response based on trust and confidence."""
        weights = trust_registry.load_weights()
        sorted_votes = sorted(
            agent_responses,
            key=lambda x: x.get("confidence", 0.0) * weights.get(x.get("agent_id"), 1.0),
            reverse=True,
        )
        return sorted_votes[0] if sorted_votes else {}
