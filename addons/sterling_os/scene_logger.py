import json, os, datetime
TRACE_FILE = "addons/sterling_os/scene_trace.json"
def log_scene(scene_id):
    data = json.load(open(TRACE_FILE))
    data["executions"].append({"scene": scene_id, "timestamp": datetime.datetime.utcnow().isoformat()})
    with open(TRACE_FILE, "w") as f: json.dump(data, f, indent=2)
