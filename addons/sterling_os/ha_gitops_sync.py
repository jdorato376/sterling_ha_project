"""Synchronize Home Assistant config from a GitHub repo."""

import subprocess
import requests
import yaml
from pathlib import Path

from .audit_logger import log_event

HA_TOKEN = ""


def sync_ha_config_from_github(repo_url: str, local_dir: str = "/config") -> None:
    """Clone or pull Home Assistant configuration from ``repo_url``."""
    path = Path(local_dir)
    if path.exists() and (path / ".git").exists():
        subprocess.run(["git", "pull"], cwd=local_dir, check=True)
    else:
        subprocess.run(["git", "clone", repo_url, local_dir], check=True)


def validate_yaml(file_path: str) -> bool:
    """Return True if ``file_path`` contains valid YAML."""
    try:
        with open(file_path, "r", encoding="utf-8") as stream:
            yaml.safe_load(stream)
        return True
    except yaml.YAMLError as exc:
        log_event("yaml_error", {"file": file_path, "error": str(exc)})
        return False


def trigger_ha_reload(url: str = "http://localhost:8123") -> None:
    """Reload Home Assistant core configuration."""
    if not HA_TOKEN:
        raise RuntimeError("HA_TOKEN not set")
    requests.post(
        f"{url}/api/services/homeassistant/reload_core_config",
        headers={"Authorization": f"Bearer {HA_TOKEN}"},
        timeout=10,
    )


