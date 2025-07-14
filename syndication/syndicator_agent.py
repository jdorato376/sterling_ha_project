from __future__ import annotations

"""Syndicator agent for scene prediction."""

import json
from pathlib import Path
from typing import List, Dict, Any
import yaml

BASE_DIR = Path(__file__).resolve().parent
CLUSTER_FILE = BASE_DIR / "scene_clusters.json"
ROUTER_FILE = BASE_DIR / "model_router.yaml"
TRUST_FILE = BASE_DIR / "model_trust_registry.json"


def load_clusters() -> List[Dict[str, Any]]:
    if CLUSTER_FILE.exists():
        try:
            return json.loads(CLUSTER_FILE.read_text())
        except Exception:
            return []
    return []


def load_router() -> Dict[str, Any]:
    if ROUTER_FILE.exists():
        try:
            return yaml.safe_load(ROUTER_FILE.read_text()) or {}
        except Exception:
            return {}
    return {}


def load_trust() -> Dict[str, Dict[str, Any]]:
    if TRUST_FILE.exists():
        try:
            return json.loads(TRUST_FILE.read_text())
        except Exception:
            return {}
    return {}


def predict_next() -> str | None:
    clusters = load_clusters()
    if clusters:
        return clusters[0].get("predicted_next")
    return None


def select_model() -> str | None:
    router = load_router()
    trust = load_trust()
    for name in router.get("route_policies", {}).get("priority", []):
        info = trust.get(name, {})
        if info.get("trust", 0) > 85 and info.get("cost", 1) <= router.get("cost_threshold", {}).get("max_cost", 0):
            return name
    return None

__all__ = [
    "load_clusters",
    "load_router",
    "load_trust",
    "predict_next",
    "select_model",
]
