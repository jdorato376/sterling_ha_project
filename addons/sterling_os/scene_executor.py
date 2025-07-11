import json
import os
from pathlib import Path
from typing import Dict

import aiohttp

HOME_ASSISTANT_URL = os.environ.get("HOME_ASSISTANT_URL", "http://localhost:8123")

from . import memory_manager

SCENE_MAP_PATH = os.environ.get(
    "SCENE_MAP_PATH",
    str(Path(__file__).resolve().parent / "scene_mapper.json"),
)


def load_scene_map() -> Dict[str, str]:
    """Return the scene mapping dictionary."""
    path = Path(SCENE_MAP_PATH)
    if path.exists():
        try:
            with path.open() as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


async def execute_scene(name: str) -> bool:
    """Trigger the configured Home Assistant scene."""
    scenes = load_scene_map()
    entity_id = scenes.get(name)
    if not entity_id:
        memory_manager.add_event(f"scene_unknown:{name}")
        return False
    url = f"{HOME_ASSISTANT_URL}/api/services/scene/turn_on"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"entity_id": entity_id}, timeout=2) as resp:
                resp.raise_for_status()
        memory_manager.add_event(f"scene:{name}")
        return True
    except Exception:
        memory_manager.add_event(f"scene_error:{name}")
        return False
