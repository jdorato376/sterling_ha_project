import datetime
import json
import os

LOG_PATH = "/config/sterling/audit_log.json"


def log_event(message: str) -> None:
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "event": message,
    }
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([log_entry], f, indent=2)
    else:
        with open(LOG_PATH, "r+") as f:
            logs = json.load(f)
            logs.append(log_entry)
            f.seek(0)
            json.dump(logs, f, indent=2)
