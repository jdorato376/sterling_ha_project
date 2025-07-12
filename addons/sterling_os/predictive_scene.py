"""Generate simple scene maps from usage history."""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict


def generate_scene_map(history: List[Dict]) -> Dict:
    """Return a basic scene map based on the current season."""
    month = datetime.now().month
    season = "winter" if month in (12, 1, 2) else "summer"
    return {"season": season, "history_sample": history[-1:]}
