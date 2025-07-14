from __future__ import annotations

"""Basic self-healing routines for Sterling OS."""

import cognitive_router
from addons.sterling_os import trust_registry, escalation_engine, scene_trace


def self_heal(intent: str, last_agent: str, error: str) -> str:
    """Attempt to reroute ``intent`` after ``last_agent`` failed."""
    trust_registry.update_weight(last_agent, -1.0)
    new_agent = cognitive_router.classify_request(intent)
    if new_agent == last_agent:
        new_agent = "fallback_agent"
    escalation_engine.escalate_scene(intent, f"{last_agent}:{error}")
    scene_trace.record_scene_status(intent, "rerouted", [last_agent, new_agent])
    return f"Rerouted to {new_agent} due to failure in {last_agent}."
