from __future__ import annotations

import difflib
import json
import logging
from pathlib import Path
from typing import Any, List, Dict


def adaptive_memory_match(query: str, persona_context: str) -> List[Dict[str, Any]]:
    """Return memory entries that best match the query."""
    memory_path = Path("addons/sterling_os/memory") / f"{persona_context}_memory.json"
    try:
        with open(memory_path, "r") as f:
            entries = json.load(f)
        matches = difflib.get_close_matches(query, [e.get("topic", "") for e in entries], n=3, cutoff=0.5)
        return [e for e in entries if e.get("topic") in matches]
    except Exception as e:
        logging.exception(f"Memory access failed for context {persona_context}")
        return [{"error": "Memory access temporarily unavailable"}]
