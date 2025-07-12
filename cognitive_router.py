"""Centralized AI routing for Sterling GPT.

This module classifies user requests and dispatches them to the
appropriate sub-agent. All routing events are logged to ``runtime_memory.json``
for later review.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Dict, List

import runtime_memory

from addons.sterling_os import intent_router
import agent_reflector

# Path to the runtime memory store is managed by ``runtime_memory``
RUNTIME_STORE = runtime_memory.RUNTIME_STORE


def log_route(query: str, agent: str, success: bool, fallback: bool) -> None:
    """Record routing decisions in ``runtime_memory.json``."""
    data = runtime_memory.read_memory()
    history = data.setdefault("route_logs", [])
    history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "agent": agent,
            "success": success,
            "fallback": fallback,
        }
    )
    runtime_memory.write_memory(data)


ROUTE_KEYWORDS: Dict[str, List[str]] = {
    "finance": ["finance", "budget", "invoice"],
    "home_automation": ["garage", "light", "scene", "home"],
    "security": ["alarm", "secure", "security"],
    "daily_briefing": ["briefing", "schedule", "agenda"],
}

# Last matched keyword for introspection
LAST_MATCH: str | None = None


def classify_request(query: str) -> str:
    """Return which internal agent should handle the query."""
    global LAST_MATCH
    lower = query.lower()
    for agent, keywords in ROUTE_KEYWORDS.items():
        for k in keywords:
            if k in lower:
                LAST_MATCH = k
                return agent
    LAST_MATCH = None
    return "general"


# Simple stub implementations for each agent

def finance_agent(query: str) -> Dict:
    return {
        "agent": "finance",
        "response": "Finance agent placeholder",
        "confidence": 0.9,
    }


def home_automation_agent(query: str) -> Dict:
    return {
        "agent": "home_automation",
        "response": intent_router.route_intent(query),
        "confidence": 0.9,
    }


def security_agent(query: str) -> Dict:
    return {
        "agent": "security",
        "response": "Security agent placeholder",
        "confidence": 0.9,
    }


def daily_briefing_agent(query: str) -> Dict:
    return {
        "agent": "daily_briefing",
        "response": "Today's briefing is empty",
        "confidence": 0.9,
    }


def general_agent(query: str) -> Dict:
    return {
        "agent": "general",
        "response": intent_router.route_intent(query),
        "confidence": 0.5,
    }


HANDLERS: Dict[str, Callable[[str], Dict]] = {
    "finance": finance_agent,
    "home_automation": home_automation_agent,
    "security": security_agent,
    "daily_briefing": daily_briefing_agent,
    "general": general_agent,
}

__all__ = [
    "handle_request",
    "classify_request",
    "log_route",
    "LAST_MATCH",
    "route_with_self_critique",
]


def handle_request(query: str) -> Dict:
    """Classify the request and dispatch to the appropriate agent."""
    agent = classify_request(query)
    handler = HANDLERS.get(agent, HANDLERS["general"])
    result = handler(query)
    result, success, fallback = agent_reflector.reflect(agent, query, result, HANDLERS["general"])
    log_route(query, agent, success, fallback)
    return result


def route_with_self_critique(query: str) -> Dict:
    """Route query twice and return the higher-confidence result.

    Both the specialized route and the general route are logged for
    auditing purposes. The returned object includes the agent name,
    response text and confidence score.
    """
    route_1 = handle_request(query)
    route_2_raw = general_agent(query)
    # log the general agent execution separately so the decision is traceable
    result2, success2, fallback2 = agent_reflector.reflect(
        "general", query, route_2_raw, HANDLERS["general"]
    )
    log_route(query, "general", success2, fallback2)

    if route_1.get("confidence", 0) >= result2.get("confidence", 0):
        return route_1
    return result2

