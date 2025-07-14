import json, os
from datetime import datetime
from addons.sterling_os.audit_logger import log_event

TRACE_PATH = "addons/sterling_os/logs/scene_trace.json"

def trace_scene(scene_id, status, notes=None):
    os.makedirs(os.path.dirname(TRACE_PATH), exist_ok=True)
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "scene_id": scene_id,
        "status": status,
        "notes": notes or {}
    }
    with open(TRACE_PATH, 'a') as f:
        f.write(json.dumps(trace) + "\n")
    log_event("trace_scene", status, {"scene": scene_id})
    print(f"📍 Scene {scene_id} - {status}")

if __name__ == "__main__":
    trace_scene("startup_check", "success", {"boot_phase": "21"})
