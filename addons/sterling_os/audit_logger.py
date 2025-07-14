import json
import os
from datetime import datetime

AUDIT_LOG = "memory/audit_log.json"


def log_event(level: str, message: str) -> None:
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
    }
    if os.path.exists(AUDIT_LOG):
        try:
            with open(AUDIT_LOG, "r") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []
    data.append(log_entry)
    # keep last 1000 entries
    data = data[-1000:]
    with open(AUDIT_LOG, "w") as f:
        json.dump(data, f, indent=2)

