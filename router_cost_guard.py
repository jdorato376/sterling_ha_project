"""Budget-aware wrapper around ``route_query``."""

from typing import Dict
from ai_router.routing_logic import route_query, estimate_cost

DEFAULT_BUDGET = 0.05


def should_escalate(model_key: str, input_tokens: int, output_tokens: int, budget: float) -> bool:
    cost = estimate_cost(model_key, input_tokens, output_tokens)
    return cost <= budget


def route_with_budget(query: str, budget: float = DEFAULT_BUDGET) -> Dict:
    result = route_query(query)
    input_tokens = len(query.split())
    output_tokens = input_tokens * 3
    if not should_escalate(result["model"], input_tokens, output_tokens, budget):
        result.update({
            "model": "free",
            "cost": 0.0,
            "response": f"Budget exceeded, using local response for: {query}",
        })
    return result


__all__ = ["should_escalate", "route_with_budget"]
