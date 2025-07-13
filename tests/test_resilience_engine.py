import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('resilience_engine', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'resilience_engine.py'))
resilience_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resilience_engine)


def test_log_and_failsafe(tmp_path, monkeypatch):
    res_log = tmp_path / 'res.json'
    fail_file = tmp_path / 'failsafe.json'
    monkeypatch.setattr(resilience_engine, 'RESILIENCE_LOG', str(res_log))
    monkeypatch.setattr(resilience_engine, 'FAILSAFE_PATH', str(fail_file))
    monkeypatch.setattr(resilience_engine, 'trust_registry', {'a': 1.0})
    monkeypatch.setattr(resilience_engine, 'log_event', lambda *a, **k: None)
    resilience_engine.log_failure('a', 'ctx', 'boom')
    assert json.loads(res_log.read_text())
    data = resilience_engine.activate_failsafe('bad')
    assert data['reason'] == 'bad'
    assert resilience_engine.is_failsafe_active() is True
    resilience_engine.reset_failsafe()
    assert not fail_file.exists()

