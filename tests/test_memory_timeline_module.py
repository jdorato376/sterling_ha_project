import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'memory_timeline',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'memory_timeline.py')
)
memory_timeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_timeline)


def test_log_event(tmp_path, monkeypatch):
    path = tmp_path / 'timeline.json'
    monkeypatch.setattr(memory_timeline.STORE, 'path', path)
    memory_timeline.log_event('test.action', 'ok', 'unit')
    data = json.loads(path.read_text())
    assert data[0]['action'] == 'test.action'
    assert data[0]['result'] == 'ok'
    assert data[0]['initiator'] == 'unit'
