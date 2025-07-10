"""Route Home Assistant voice intents to Sterling OS."""

import os
from typing import Optional

from .main import interpret_intent
from . import memory_manager

_OLLAMA_CACHE: dict[str, str] = {}


def _local_llm_response(prompt: str) -> str:
    """Return a response from the local Ollama model if available."""
    if prompt in _OLLAMA_CACHE:
        return _OLLAMA_CACHE[prompt]

    try:
        import ollama
        model = os.environ.get("OLLAMA_MODEL", "llama3")
        memory_manager.add_event(f"_ollama_fallback:{prompt}")
        result = ollama.generate(model=model, prompt=prompt)
        reply = result.get("response", "").strip()
        if reply:
            _OLLAMA_CACHE[prompt] = reply
            memory_manager.add_event(f"_local_llm_response:{reply}")
        return reply
    except Exception:
        return ""


def contextual_suggestion(phrase: str) -> Optional[str]:
    """Return a contextual intent suggestion from memory."""
    events = memory_manager.get_recent_phrases(limit=20)
    phrase_tokens = set(phrase.lower().split())
    best_match: Optional[str] = None
    best_score = 0
    for evt in reversed(events):
        text = evt.get("event", "")
        if ":" in text:
            _, val = text.split(":", 1)
        else:
            val = text
        if val.strip().lower() == phrase.lower():
            continue
        val_clean = val.replace("|", " ").replace(":", " ")
        tokens = set(val_clean.lower().split())
        score = len(phrase_tokens & tokens)
        if phrase.lower() in val_clean.lower() or val_clean.lower() in phrase.lower():
            score += 1
        if score > best_score and score > 0:
            best_score = score
            best_match = val
    if best_match:
        guess = interpret_intent(best_match)
        if guess != "I'm not sure how to help with that.":
            memory_manager.add_event(f"_context_hint:{best_match}")
            return guess
        memory_manager.add_event(f"_context_hint:{best_match}")
        return f"Did you mean '{best_match}'?"
    return None



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
        suggestion = contextual_suggestion(phrase)
        if suggestion:
            return suggestion
        llm_reply = _local_llm_response(phrase)
        if llm_reply:
            return llm_reply

    return "I'm not sure, but here's what I can try..."
