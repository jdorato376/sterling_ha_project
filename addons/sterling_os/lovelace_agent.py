"""Utility functions for Lovelace UI integration."""


def get_status():
    return "idle"


def get_task_queue():
    return []


def respond_to_input(text: str) -> str:
    """Return a response string routed through the intent router."""
    from . import intent_router

    return intent_router.route_intent(text)
