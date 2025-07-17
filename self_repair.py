import json
from pathlib import Path
from typing import List

DIAG_LOG = Path("diagnostics_log.json")
BACKUP_DIR = Path("backups")


def scan_for_errors() -> List[str]:
    """Return a list of error strings from the diagnostics log."""
    if not DIAG_LOG.exists():
        return []
    try:
        data = json.loads(DIAG_LOG.read_text())
    except Exception:
        return []
    errors: List[str] = []
    for entry in data:
        for risk in entry.get("risks", []):
            if "error" in risk.lower():
                errors.append(risk)
    return errors


def restore_file(target: Path) -> bool:
    """Restore ``target`` from the backups directory if available."""
    backup = BACKUP_DIR / target.name
    if backup.exists():
        target.write_text(backup.read_text())
        return True
    return False


def self_heal(target: Path) -> bool:
    """Attempt to heal ``target`` based on diagnostics."""
    if not scan_for_errors():
        return False
    return restore_file(target)


__all__ = ["scan_for_errors", "restore_file", "self_heal"]
