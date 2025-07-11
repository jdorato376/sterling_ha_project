import json
from git_diff_analyzer import get_last_commit_diff
from behavior_modulator import adjust_behavior_based_on_diff


def update_runtime_config():
    """Apply behavioral adaptations based on the latest git diff."""
    diff_data = get_last_commit_diff()
    if "error" in diff_data:
        print(diff_data["error"])
        return
    updated_behavior = adjust_behavior_based_on_diff(diff_data)
    try:
        with open("runtime_memory.json", "w") as f:
            json.dump(updated_behavior, f, indent=2)
        print("✅ Runtime behavior updated.")
    except Exception as e:
        print(f"❌ Failed to update runtime config: {e}")
