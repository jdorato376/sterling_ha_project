from __future__ import annotations

"""Persist and query scene status across reboots."""

from pathlib import Path
from typing import Dict

from json_store import JSONStore

_STATUS_STORE = JSONStore(Path(__file__).resolve().parent / "scene_status.json", default={})


def update_status(scene_id: str, status: str) -> Dict[str, str]:
    data = _STATUS_STORE.read()
    data[scene_id] = status
    _STATUS_STORE.write(data)
    return data


def get_status(scene_id: str) -> str:
    return _STATUS_STORE.read().get(scene_id, "")


def all_statuses() -> Dict[str, str]:
    return _STATUS_STORE.read()
