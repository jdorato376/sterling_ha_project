"""Timeline logging for executed commands."""
from __future__ import annotations

from . import memory_manager


def record(command: str) -> None:
    """Log a command invocation to the timeline."""
    memory_manager.add_event(f"cmd:{command}")
