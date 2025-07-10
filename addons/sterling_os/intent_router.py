"""Route Home Assistant voice intents to Sterling OS."""

from .main import interpret_intent
from . import memory_manager


def route_intent(phrase: str) -> str:
    """Return a response for the given spoken phrase."""
    # Check if the phrase directly matches a known intent key
    direct = interpret_intent(phrase)
    if direct != "I'm not sure how to help with that.":
        memory_manager.add_event(f"intent:{phrase}")
        return direct

    # Basic history-based fallback: if user asks about recent events
    if "last" in phrase.lower() and "friday" in phrase.lower():
        events = memory_manager.get_timeline()
        if events:
            latest = events[-1]
            return f"Last event: {latest['event']} at {latest['timestamp']}"

    memory_manager.add_event(f"unknown:{phrase}")
    return "I'm not sure, but here\u2019s what I can try..."
