def adjust_behavior_based_on_diff(diff_data):
    """Map git diff changes to runtime behavior config."""
    behavior = {
        "monitor_frequency_sec": 30,
        "test_layer": False,
        "log_heartbeat": False,
    }
    for file in diff_data.get("modified", []):
        if "app.py" in file:
            behavior["monitor_frequency_sec"] = 10
        if "test" in file or "tests" in file:
            behavior["test_layer"] = True
        if "uptime_tracker" in file:
            behavior["log_heartbeat"] = True
    return behavior
