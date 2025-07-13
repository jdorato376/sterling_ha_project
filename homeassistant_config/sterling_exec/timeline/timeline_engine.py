import json
import datetime

SCENE_TRACE_PATH = "/config/sterling_exec/timeline/scene_trace.json"
LOG_PATH = "/config/sterling_exec/timeline/timeline_log.json"


def log_event(event_type, description, context=None):
    timestamp = datetime.datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "event": event_type,
        "description": description,
        "context": context or {}
    }

    try:
        with open(SCENE_TRACE_PATH, "r") as f:
            trace = json.load(f)
    except Exception:
        trace = {"scenes": [], "last_scene": None, "scene_log": []}

    trace["scene_log"].append(entry)
    trace["last_scene"] = entry

    with open(SCENE_TRACE_PATH, "w") as f:
        json.dump(trace, f, indent=2)

    try:
        with open(LOG_PATH, "r") as f:
            log_data = json.load(f)
    except Exception:
        log_data = []

    log_data.append(entry)

    with open(LOG_PATH, "w") as f:
        json.dump(log_data, f, indent=2)

    print(f"[TRACE] Logged: {event_type} – {description}")


if __name__ == "__main__":
    log_event("bootstrap", "Sterling Timeline Engine initialized")
