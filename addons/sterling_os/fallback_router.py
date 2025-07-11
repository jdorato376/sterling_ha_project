import os

from . import memory_manager


def _gemini_request(prompt: str) -> str:
    """Call the remote Gemini API. This stub intentionally raises to simulate
    network issues in tests."""
    raise RuntimeError("gemini failure")


def _ollama_request(prompt: str) -> str:
    """Return a response from the local Ollama model if installed."""
    try:
        import ollama
    except Exception:
        return ""
    model = os.environ.get("OLLAMA_MODEL", "llama3")
    result = ollama.generate(model=model, prompt=prompt)
    return result.get("response", "").strip()


def route_query(prompt: str) -> str:
    """Return a reply using Gemini with Ollama fallback."""
    try:
        reply = _gemini_request(prompt)
        if reply:
            memory_manager.add_event(f"gemini:{prompt}")
            return reply
    except Exception:
        pass

    try:
        reply = _ollama_request(prompt)
        if reply:
            memory_manager.add_event(f"_ollama_fallback:{prompt}")
            return reply
    except Exception:
        pass
    return "I'm not sure."
