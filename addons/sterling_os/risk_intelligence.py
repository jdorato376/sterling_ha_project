"""Basic risk detection for logs and config drift."""
from __future__ import annotations

from typing import List


def detect_risks(log_lines: List[str]) -> List[str]:
    """Return lines that appear risky."""
    return [line for line in log_lines if "error" in line.lower()]
