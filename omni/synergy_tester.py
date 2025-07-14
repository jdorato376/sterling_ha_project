from __future__ import annotations

"""Synthetic tests for agent synergy."""

from typing import List, Dict

try:  # allow running without package context
    from . import agent_linker
    from .agent_linker import register_agent, update_heartbeat
    from .timeline_orchestrator import fuse_timelines
except Exception:  # pragma: no cover - fallback for direct execution
    import importlib.util
    from pathlib import Path
    _base = Path(__file__).resolve().parent
    _spec_l = importlib.util.spec_from_file_location(
        "agent_linker", _base / "agent_linker.py"
    )
    agent_linker = importlib.util.module_from_spec(_spec_l)
    _spec_l.loader.exec_module(agent_linker)
    register_agent = agent_linker.register_agent
    update_heartbeat = agent_linker.update_heartbeat
    _spec_t = importlib.util.spec_from_file_location(
        "timeline_orchestrator", _base / "timeline_orchestrator.py"
    )
    timeline_orchestrator = importlib.util.module_from_spec(_spec_t)
    _spec_t.loader.exec_module(timeline_orchestrator)
    fuse_timelines = timeline_orchestrator.fuse_timelines


def run_test() -> List[Dict]:
    """Run a simple synergy check across two agents."""
    register_agent("alpha", ["ping"])
    register_agent("beta", ["pong"])
    update_heartbeat("alpha")
    update_heartbeat("beta")
    timeline_a = [{"task": "alpha", "timestamp": 1}]
    timeline_b = [{"task": "beta", "timestamp": 2}]
    return fuse_timelines(timeline_a, timeline_b)

__all__ = ["run_test"]
