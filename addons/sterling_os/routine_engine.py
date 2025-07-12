from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional
import importlib



def _is_weekday_morning(now: datetime) -> bool:
    return now.weekday() < 5 and 6 <= now.hour < 9


def evaluate_routines(
    now: Optional[datetime] = None,
    states: Optional[Dict[str, str]] = None,
    events: Optional[list] = None,
) -> Optional[str]:
    """Trigger routines based on simple context rules.

    Parameters
    ----------
    now : datetime, optional
        Current time, defaults to ``datetime.now()``.
    states : dict, optional
        Mapping of Home Assistant entity states.
    events : list, optional
        Recent calendar event titles.
    Returns
    -------
    str or None
        Name of the scene executed or ``None``.
    """
    now = now or datetime.now()
    states = states or {}
    events = events or []

    scene_executor = importlib.import_module('addons.sterling_os.scene_executor')
    memory_manager = importlib.import_module('addons.sterling_os.memory_manager')

    if _is_weekday_morning(now):
        if (
            states.get("bedroom_lights") == "on"
            and states.get("watch_active")
        ):
            scene_executor.execute_scene("MorningOpsScene")
            memory_manager.add_event("routine:MorningOpsScene")
            return "MorningOpsScene"
    return None
