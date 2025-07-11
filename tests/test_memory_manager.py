import json
import importlib.util
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('memory_manager', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'memory_manager.py'))
memory_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_manager)


def test_add_and_reset(tmp_path, monkeypatch):
    mem = tmp_path / 'memory.json'
    monkeypatch.setattr(memory_manager.MEMORY_STORE, 'path', mem)
    memory_manager.add_event('test:event')
    assert json.loads(mem.read_text())[0]['event'] == 'test:event'
    memory_manager.reset_memory()
    assert json.loads(mem.read_text()) == []


def test_log_phrase_dedup(tmp_path, monkeypatch):
    mem = tmp_path / 'memory.json'
    monkeypatch.setattr(memory_manager.MEMORY_STORE, 'path', mem)
    memory_manager.log_phrase('hello')
    memory_manager.log_phrase('hello')
    data = json.loads(mem.read_text())
    assert len(data) == 1
    assert data[0]['event'].startswith('phrase:')


def test_get_recent_phrases(tmp_path, monkeypatch):
    mem = tmp_path / 'memory.json'
    monkeypatch.setattr(memory_manager.MEMORY_STORE, 'path', mem)
    for i in range(3):
        memory_manager.log_phrase(f'hello{i}')
    phrases = memory_manager.get_recent_phrases(limit=2)
    assert len(phrases) == 2
    assert all(p['event'].startswith('phrase:') for p in phrases)

