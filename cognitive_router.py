"""Centralized AI routing for Sterling GPT.

This module classifies user requests and dispatches them to the
appropriate sub-agent. All routing events are logged to ``runtime_memory.json``
for later review.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List

from json_store import JSONStore

from addons.sterling_os import intent_router
import agent_reflector

# Path to the runtime memory store
RUNTIME_STORE = JSONStore(Path("runtime_memory.json"))


def log_route(query: str, agent: str, success: bool, fallback: bool) -> None:
    """Record routing decisions in ``runtime_memory.json``."""
    data = RUNTIME_STORE.read()
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
    RUNTIME_STORE.write(data)


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
    return {"agent": "finance", "response": "Finance agent placeholder"}


def home_automation_agent(query: str) -> Dict:
    return {"agent": "home_automation", "response": intent_router.route_intent(query)}


def security_agent(query: str) -> Dict:
    return {"agent": "security", "response": "Security agent placeholder"}


def daily_briefing_agent(query: str) -> Dict:
    return {"agent": "daily_briefing", "response": "Today's briefing is empty"}


HANDLERS: Dict[str, Callable[[str], Dict]] = {
    "finance": finance_agent,
    "home_automation": home_automation_agent,
    "security": security_agent,
    "daily_briefing": daily_briefing_agent,
    "general": lambda q: {"agent": "general", "response": intent_router.route_intent(q)},
}

__all__ = [
    "handle_request",
    "classify_request",
    "log_route",
    "LAST_MATCH",
]


def handle_request(query: str) -> Dict:
    """Classify the request and dispatch to the appropriate agent."""
    agent = classify_request(query)
    handler = HANDLERS.get(agent, HANDLERS["general"])
    result = handler(query)
    result, success, fallback = agent_reflector.reflect(agent, query, result, HANDLERS["general"])
    log_route(query, agent, success, fallback)
    return result

