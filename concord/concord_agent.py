from __future__ import annotations
"""Minimal Concord agent for multi-model grading."""

import json
from pathlib import Path
from typing import Dict, Any
import yaml

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "sandbox_registry.yaml"
GRADEBOOK_FILE = BASE_DIR / "model_gradebook.json"


def load_registry() -> Dict[str, Any]:
    if REGISTRY_FILE.exists():
        try:
            return yaml.safe_load(REGISTRY_FILE.read_text()) or {}
        except Exception:
            return {}
    return {}


def load_gradebook() -> Any:
    if GRADEBOOK_FILE.exists():
        try:
            return json.loads(GRADEBOOK_FILE.read_text())
        except Exception:
            return []
    return []


def grade_responses(responses: Dict[str, float]) -> str | None:
    if not responses:
        return None
    return max(responses.items(), key=lambda x: x[1])[0]


def record_grade(prompt_id: str, responses: Dict[str, float]) -> str | None:
    winner = grade_responses(responses)
    gradebook = load_gradebook()
    gradebook.append({"prompt_id": prompt_id, "responses": responses, "winner": winner})
    GRADEBOOK_FILE.write_text(json.dumps(gradebook, indent=2))
    return winner

__all__ = [
    "load_registry",
    "load_gradebook",
    "grade_responses",
    "record_grade",
]
