import importlib.util
import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec_router = importlib.util.spec_from_file_location('cognitive_router', os.path.join(os.path.dirname(__file__), '..', 'cognitive_router.py'))
cognitive_router = importlib.util.module_from_spec(spec_router)
spec_router.loader.exec_module(cognitive_router)

spec_reflector = importlib.util.spec_from_file_location('agent_reflector', os.path.join(os.path.dirname(__file__), '..', 'agent_reflector.py'))
agent_reflector = importlib.util.module_from_spec(spec_reflector)
spec_reflector.loader.exec_module(agent_reflector)


def test_escalation_trigger(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    mem.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', mem)
    monkeypatch.setattr(agent_reflector.RUNTIME_STORE, 'path', mem)
    monkeypatch.setattr(cognitive_router.agent_reflector.RUNTIME_STORE, 'path', mem)

    res = cognitive_router.handle_request('toggle kitchen light')
    data = json.loads(mem.read_text())
    assert res['agent'] == 'general'
    assert data['fallback_triggered'] is True
    assert data['agent_trace'][-1]['escalated_to'] == 'general'


def test_success_logging(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    mem.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', mem)
    monkeypatch.setattr(agent_reflector.RUNTIME_STORE, 'path', mem)
    monkeypatch.setattr(cognitive_router.agent_reflector.RUNTIME_STORE, 'path', mem)

    res = cognitive_router.handle_request('show my budget')
    data = json.loads(mem.read_text())
    assert res['agent'] == 'finance'
    assert data['last_success'] is True
    assert data['fallback_triggered'] is False
    assert data['agent_trace'][-1]['success'] is True
