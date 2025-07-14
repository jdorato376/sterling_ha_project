"""Simple memory compression utility."""
from __future__ import annotations

from typing import List


def compress_logs(logs: List[str]) -> str:
    if not logs:
        return ""
    # naive compression: join first and last
    if len(logs) == 1:
        return logs[0]
    return f"{logs[0]} ... {logs[-1]}"

__all__ = ["compress_logs"]
