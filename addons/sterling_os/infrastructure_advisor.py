"""Simple resource usage advisor."""
from __future__ import annotations


def advise(cpu_load: float, mem_usage: float, threshold: float = 0.9) -> str:
    """Return 'scale' if utilization exceeds threshold."""
    if cpu_load > threshold or mem_usage > threshold:
        return "scale"
    return "ok"
