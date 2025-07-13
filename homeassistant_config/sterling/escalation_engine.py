import json
import os

from .audit_logger import log_event

SENTINEL_CONFIG = "/config/sterling/sentinel_config.yaml"


def load_threshold() -> float:
    if os.path.exists(SENTINEL_CONFIG):
        with open(SENTINEL_CONFIG, "r") as f:
            for line in f:
                if "confidence_threshold" in line:
                    return float(line.split(":")[1].strip())
    return 0.65


def escalate_if_needed(task: str, confidence: float) -> bool:
    threshold = load_threshold()
    if confidence < threshold:
        log_event(f"[ESCALATION] Task '{task}' escalated at {confidence} confidence.")
        return True
    log_event(f"[NORMAL] Task '{task}' proceeded at {confidence} confidence.")
    return False
