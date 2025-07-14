from datetime import datetime
import json
import os

from addons.sterling_os.audit_logger import log_event
from addons.sterling_os.trust_registry import trust_registry

RESILIENCE_LOG = "memory/resilience_log.json"
FAILSAFE_PATH = "memory/failsafe_state.json"


def load_resilience_log():
    if os.path.exists(RESILIENCE_LOG):
        with open(RESILIENCE_LOG, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def save_resilience_log(log):
    with open(RESILIENCE_LOG, "w") as f:
        json.dump(log, f, indent=2)


def log_failure(agent: str, context: str, description: str) -> None:
    log = load_resilience_log()
    entry = {
        "agent": agent,
        "context": context,
        "description": description,
        "timestamp": datetime.now().isoformat(),
    }
    key = f"{agent}_{datetime.now().timestamp()}"
    log[key] = entry
    save_resilience_log(log)
    log_event("FAILURE", f"{agent} failed in {context}: {description}")


def activate_failsafe(reason: str):
    data = {
        "activated_at": datetime.now().isoformat(),
        "reason": reason,
        "trust_snapshot": trust_registry,
    }
    with open(FAILSAFE_PATH, "w") as f:
        json.dump(data, f, indent=2)
    log_event("FAILSAFE", reason)
    return data


def reset_failsafe():
    if os.path.exists(FAILSAFE_PATH):
        os.remove(FAILSAFE_PATH)
        log_event("FAILSAFE_RESET", "System back to normal")


def is_failsafe_active() -> bool:
    return os.path.exists(FAILSAFE_PATH)


def resilience_status():
    return {
        "failsafe_active": is_failsafe_active(),
        "failures_recorded": len(load_resilience_log()),
    }
