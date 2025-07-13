"""Route intents based on dynamic trust scores."""

from .trust_registry import trust_registry
from .fallback_router import fallback_to_safe_mode

AGENT_MAP = {
    "codex": "http://localhost:8000/codex",
    "gemini": "http://localhost:8000/gemini",
    "home_assistant": "http://localhost:8000/ha",
    "fallback_agent": "http://localhost:8000/fallback",
}

TRUST_THRESHOLD = 0.65


def send_to_agent(agent_id: str, intent: str, context: str) -> dict:
    """Placeholder for real agent API calls."""
    return {
        "agent": agent_id,
        "intent": intent,
        "context": context,
        "response": f"Handled by {agent_id}",
    }


def smart_route(intent: str, context: str) -> dict:
    """Return the first high-trust agent response or safe fallback."""
    weighted = sorted(trust_registry.items(), key=lambda x: x[1], reverse=True)
    for agent_id, score in weighted:
        if score >= TRUST_THRESHOLD:
            try:
                return send_to_agent(agent_id, intent, context)
            except Exception as exc:  # pragma: no cover - placeholder logging
                print(f"[!] {agent_id} failed: {exc}")
                continue
    return fallback_to_safe_mode(intent)
