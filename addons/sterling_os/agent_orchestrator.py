"""Vote-based agent arbitration for Sterling OS.

This module exposes two layers of decision making:

``handle_query`` provides a simple escalation chain used by existing tests.
``arbitrate`` implements a weighted voting model for Phase 5 features.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

from . import memory_manager
from .intent_router import _local_llm_response


def _gemini_response(query: str) -> str:
    """Stub for remote Gemini API. Raises to simulate failure."""
    raise RuntimeError("gemini unavailable")


def arbitrate(
    responses: Dict[str, str],
    trust: Dict[str, float],
    override: Optional[str] = None,
) -> str:
    """Return the chosen response via weighted trust voting."""
    if override and override in responses:
        return responses[override]

    weighted = {
        agent: trust.get(agent, 0.0) for agent in responses
    }
    if not weighted:
        return ""
    best_agent = max(weighted, key=weighted.get)
    return responses[best_agent]


def handle_query(query: str) -> Dict:
    """Return a structured response using escalation chain."""
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        reply = _gemini_response(query)
        if reply:
            memory_manager.add_event(f"_thread_resolution:{reply}")
            return {
                "response": reply,
                "agent_used": "gemini",
                "timestamp": timestamp,
                "success_status": True,
                "confidence_score": 0.9,
            }
    except Exception:
        pass

    reply = _local_llm_response(query)
    if reply:
        return {
            "response": reply,
            "agent_used": "ollama",
            "timestamp": timestamp,
            "success_status": True,
            "confidence_score": 0.5,
        }

    return {
        "response": "I'm not sure, but here's what I can try...",
        "agent_used": "static",
        "timestamp": timestamp,
        "success_status": False,
        "confidence_score": 0.0,
    }


def handle_query_vote(query: str, trust: Dict[str, float], override: Optional[str] = None) -> Dict:
    """Return a structured response using vote-based arbitration."""
    timestamp = datetime.now(timezone.utc).isoformat()

    candidates = {}
    try:
        candidates["gemini"] = _gemini_response(query)
    except Exception:
        pass

    candidates["core"] = _local_llm_response(query)

    if not candidates:
        return {
            "response": "No agent response available",
            "agent_used": "none",
            "timestamp": timestamp,
            "success_status": False,
            "confidence_score": 0.0,
        }

    agent = "core"
    if len(candidates) > 1:
        agent = max(candidates, key=lambda a: trust.get(a, 0.0))
    if override and override in candidates:
        agent = override

    memory_manager.add_event(f"agent_vote:{agent}")
    return {
        "response": candidates[agent],
        "agent_used": agent,
        "timestamp": timestamp,
        "success_status": True,
        "confidence_score": trust.get(agent, 0.0),
    }
