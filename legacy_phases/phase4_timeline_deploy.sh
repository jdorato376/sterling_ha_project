#!/usr/bin/env bash
# Sterling GPT Phase 4: Timeline Engine + Scene Trace Intelligence
set -euo pipefail

echo "🚀 PHASE 4: Timeline Engine + Scene Trace Intelligence Deploy"

mkdir -p /config/sterling_exec/timeline
cd /config/sterling_exec/timeline

cat <<'JSON' > scene_trace.json
{
  "scenes": [],
  "last_scene": null,
  "scene_log": []
}
JSON

cat <<'PY' > timeline_engine.py
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
PY

chmod +x timeline_engine.py

# Manual test run
echo "🔁 Running Timeline Engine Test"
python3 /config/sterling_exec/timeline/timeline_engine.py

# Wire into git pull hook
cat <<'HOOK' >> /config/sterling_exec/hooks/git_post_pull.sh

# === Phase 4: Timeline Hook Trigger ===
echo "📜 Updating Sterling Timeline"
python3 /config/sterling_exec/timeline/timeline_engine.py
HOOK

chmod +x /config/sterling_exec/hooks/git_post_pull.sh

# Register initial scene event
python3 - <<'PY'
from timeline_engine import log_event
log_event('system_boot', 'Sterling HAOS Boot Detected', {'phase': '4', 'status': 'clean'})
PY

echo "✅ Sterling Phase 4: Timeline Engine & Scene Tracing Active"
