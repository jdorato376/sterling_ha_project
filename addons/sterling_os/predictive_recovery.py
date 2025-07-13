"""Simple checkpointing for scene recovery."""

import json
import os
import time

RECOVERY_LOG = "/config/.codex_recovery.json"
MAX_CHECKPOINTS = 25


def save_checkpoint(scene_id: str, data: dict) -> None:
    """Append a checkpoint entry to the recovery log."""
    checkpoint = {
        "scene_id": scene_id,
        "data": data,
        "timestamp": time.time(),
    }
    history = []
    if os.path.exists(RECOVERY_LOG):
        with open(RECOVERY_LOG, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []
    history.append(checkpoint)
    if len(history) > MAX_CHECKPOINTS:
        history = history[-MAX_CHECKPOINTS:]
    with open(RECOVERY_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def get_last_checkpoint(scene_id: str | None = None) -> dict | None:
    """Return the most recent checkpoint or last one for ``scene_id``."""
    if not os.path.exists(RECOVERY_LOG):
        return None
    with open(RECOVERY_LOG, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except Exception:
            return None
    if scene_id:
        for item in reversed(history):
            if item.get("scene_id") == scene_id:
                return item
    return history[-1] if history else None
