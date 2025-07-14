from __future__ import annotations

from git_diff_analyzer import get_last_commit_diff
from behavior_modulator import adjust_behavior_based_on_diff
import runtime_memory
from json_store import JSONStoreError
import shutil
import time
from pathlib import Path

MAX_EVENTS = 500


def _truncate_memory(data: dict) -> dict:
    """Truncate event history if it grows beyond ``MAX_EVENTS``."""
    for key in ("agent_trace", "route_logs"):
        events = data.get(key, [])
        if len(events) > MAX_EVENTS:
            data[key] = events[-MAX_EVENTS:]
    return data


def _rotate_backups(path: Path, max_keep: int = 3) -> None:
    """Rotate backup files ``runtime_memory.bak.N``."""
    for i in range(max_keep, 0, -1):
        src = path.with_suffix(f".bak.{i}")
        dst = path.with_suffix(f".bak.{i+1}")
        if src.exists():
            src.rename(dst)
    bak = path.with_suffix(".bak.1")
    try:
        shutil.copy(path, bak)
    except Exception:
        pass


def safe_write_memory(data: dict, retries: int = 3) -> None:
    """Attempt to write memory with fallback and backups."""
    _rotate_backups(runtime_memory.RUNTIME_STORE.path)
    attempt = 0
    while attempt < retries:
        try:
            runtime_memory.RUNTIME_STORE.write(data)
            return
        except JSONStoreError:
            attempt += 1
            time.sleep(0.1)
    runtime_memory.alert_admin("Memory write failed", "fallback to default")
    runtime_memory.RUNTIME_STORE.write(runtime_memory.RUNTIME_STORE.default)



def update_runtime_config() -> None:
    """Apply behavioral adaptations based on the latest git diff."""
    diff_data = get_last_commit_diff()
    if "error" in diff_data:
        print(diff_data["error"])
        return
    updated_behavior = adjust_behavior_based_on_diff(diff_data)
    try:
        data = runtime_memory.read_memory()
        data.update(updated_behavior)
        data = _truncate_memory(data)
        safe_write_memory(data)
        print("✅ Runtime behavior updated.")
    except Exception as exc:  # pragma: no cover - log error only
        print(f"❌ Failed to update runtime config: {exc}")
