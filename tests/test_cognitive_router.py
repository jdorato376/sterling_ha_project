import importlib.util
import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('cognitive_router', os.path.join(os.path.dirname(__file__), '..', 'cognitive_router.py'))
cognitive_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cognitive_router)


def test_handle_request_logs(tmp_path, monkeypatch):
    log_file = tmp_path / 'runtime_memory.json'
    log_file.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', log_file)

    res = cognitive_router.handle_request('give me a daily briefing')
    assert res['agent'] == 'daily_briefing'

    data = json.loads(log_file.read_text())
    assert data['route_logs'][-1]['agent'] == 'daily_briefing'


def test_finance_classification(tmp_path, monkeypatch):
    log_file = tmp_path / 'runtime_memory.json'
    log_file.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', log_file)

    res = cognitive_router.handle_request('show my budget report')
    assert res['agent'] == 'finance'


def test_unknown_falls_back_to_general(tmp_path, monkeypatch):
    log_file = tmp_path / 'runtime_memory.json'
    log_file.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', log_file)

    res = cognitive_router.handle_request('tell me a joke')
    assert res['agent'] == 'general'


def test_home_automation_classification(tmp_path, monkeypatch):
    log_file = tmp_path / 'runtime_memory.json'
    log_file.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', log_file)
    monkeypatch.setattr(cognitive_router.agent_reflector.RUNTIME_STORE, 'path', log_file)

    res = cognitive_router.handle_request('toggle kitchen light')
    # Final result falls back to general due to schema mismatch
    assert cognitive_router.LAST_MATCH == 'light'
    data = json.loads(log_file.read_text())
    assert data['route_logs'][-1]['agent'] == 'home_automation'
    assert data['fallback_triggered'] is True


def test_security_classification(tmp_path, monkeypatch):
    log_file = tmp_path / 'runtime_memory.json'
    log_file.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', log_file)
    monkeypatch.setattr(cognitive_router.agent_reflector.RUNTIME_STORE, 'path', log_file)

    res = cognitive_router.handle_request('arm the security system')
    assert res['agent'] == 'security'
    data = json.loads(log_file.read_text())
    assert data['route_logs'][-1]['agent'] == 'security'

