"""Self test script for Platinum Dominion."""

from __future__ import annotations

import json
import sys
import yaml

from .governor import TRUST_FILE as GOVERNOR_TRUST_FILE, LOGBOOK_FILE as GOVERNOR_LOGBOOK_FILE

# re-export paths for easier test patching
TRUST_FILE = GOVERNOR_TRUST_FILE
LOGBOOK_FILE = GOVERNOR_LOGBOOK_FILE


def run_tests() -> bool:
    try:
        data = json.loads(TRUST_FILE.read_text()) if TRUST_FILE.exists() else {}
        if not all(0.0 <= float(v) <= 1.0 for v in data.values()):
            return False
    except Exception:
        return False
    try:
        if LOGBOOK_FILE.exists():
            yaml.safe_load(LOGBOOK_FILE.read_text())
    except Exception:
        return False
    return True


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
