"""Route Home Assistant voice intents to Sterling OS."""

from .main import interpret_intent
from . import memory_manager



def route_intent(phrase: str, fallback: bool = False) -> str:
    """Return a response for the given spoken phrase."""

    # Check if the phrase directly matches a known intent key
    direct = interpret_intent(phrase)
    if direct != "I'm not sure how to help with that.":
        memory_manager.log_phrase(phrase, intent=phrase)
        memory_manager.add_event(f"intent:{phrase}")
        return direct

    # Basic history-based fallback: if user asks about recent events
    if "last" in phrase.lower() and "friday" in phrase.lower():
        events = memory_manager.get_timeline()
        if events:
            latest = events[-1]
            return f"Last event: {latest['event']} at {latest['timestamp']}"

    memory_manager.log_phrase(phrase)
    memory_manager.add_event(f"unknown:{phrase}")

    if fallback:
        memory_manager.add_event(f"fallback:{phrase}")
        events = memory_manager.get_recent_phrases(limit=20)
        phrase_tokens = set(phrase.lower().split())
        best_match = None
        best_score = 0
        for evt in reversed(events):
            text = evt.get("event", "")
            if ":" in text:
                _, val = text.split(":", 1)
            else:
                val = text
            tokens = set(val.lower().split())
            score = len(phrase_tokens & tokens)
            if score > best_score and score > 0:
                best_score = score
                best_match = val

        if best_match:
            guess = interpret_intent(best_match)
            if guess != "I'm not sure how to help with that.":
                return guess
            return f"Did you mean '{best_match}'?"

    return "I'm not sure, but here's what I can try..."
