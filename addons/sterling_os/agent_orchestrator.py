from __future__ import annotations

"""Simple agent escalation logic for Sterling OS."""

from datetime import datetime, timezone
from typing import Dict

from . import memory_manager
from .intent_router import _local_llm_response


def _gemini_response(query: str) -> str:
    """Stub for remote Gemini API. Raises to simulate failure."""
    raise RuntimeError("gemini unavailable")


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
