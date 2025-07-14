"""Rollback engine for failed threads."""
from __future__ import annotations

from typing import Dict


def rollback_thread(name: str) -> Dict[str, str]:
    """Return a simple rollback result."""
    return {"thread": name, "status": "reverted"}

__all__ = ["rollback_thread"]
