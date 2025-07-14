"""Simplified GitOps engine for development mode."""

from pathlib import Path


def run(command: str, user_confirm: bool, enabled: bool):
    """Pretend to apply a code change if enabled and confirmed."""
    if not enabled or not user_confirm:
        return {"status": "skipped"}

    temp_file = Path("/tmp/devgpt_change.txt")
    temp_file.write_text(f"COMMAND: {command}\n")
    return {"status": "ok", "file": str(temp_file)}


def auto_update(user_confirm: bool = False):
    """Backward compatible wrapper."""
    return run("auto", user_confirm, True)
