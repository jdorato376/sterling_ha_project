import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location('threads.timeline_guard', os.path.join(os.path.dirname(__file__), '..', 'threads', 'timeline_guard.py'))
timeline_guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timeline_guard)


def test_lock_unlock(tmp_path, monkeypatch):
    registry = tmp_path / 'reg.json'
    monkeypatch.setattr(timeline_guard, 'REGISTRY_FILE', registry)
    registry.write_text('{}')
    assert not timeline_guard.is_locked('home')
    registry.write_text('{"home": {"locked": false}}')
    assert timeline_guard.lock_thread('home') is True
    assert timeline_guard.is_locked('home') is True
    assert timeline_guard.unlock_thread('home') is True
    assert timeline_guard.is_locked('home') is False
