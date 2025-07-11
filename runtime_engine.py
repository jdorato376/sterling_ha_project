from __future__ import annotations

from git_diff_analyzer import get_last_commit_diff
from behavior_modulator import adjust_behavior_based_on_diff
from json_store import JSONStore
from pathlib import Path

RUNTIME_STORE = JSONStore(Path("runtime_memory.json"))


def update_runtime_config() -> None:
    """Apply behavioral adaptations based on the latest git diff."""
    diff_data = get_last_commit_diff()
    if "error" in diff_data:
        print(diff_data["error"])
        return
    updated_behavior = adjust_behavior_based_on_diff(diff_data)
    try:
        RUNTIME_STORE.write(updated_behavior)
        print("✅ Runtime behavior updated.")
    except Exception as exc:  # pragma: no cover - log error only
        print(f"❌ Failed to update runtime config: {exc}")
