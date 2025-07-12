"""Utility for applying YAML patches without downtime."""
from __future__ import annotations

from typing import Dict
import yaml


def apply_patch(config_yaml: str, patch: Dict) -> str:
    """Apply a simple dictionary patch to YAML config."""
    data = yaml.safe_load(config_yaml) or {}
    data.update(patch)
    return yaml.safe_dump(data, sort_keys=False)
