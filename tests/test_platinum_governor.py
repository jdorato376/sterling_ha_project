import importlib.util
import os
import sys
import types
import json
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('platinum.governor', os.path.join(os.path.dirname(__file__), '..', 'platinum', 'governor.py'))
platinum_governor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platinum_governor)

spec_e = importlib.util.spec_from_file_location('addons.sterling_os.escalation_engine', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'escalation_engine.py'))
escalation_engine = importlib.util.module_from_spec(spec_e)
spec_e.loader.exec_module(escalation_engine)


def test_check_threshold(tmp_path, monkeypatch):
    trust_file = tmp_path / 'trust.json'
    trust_file.write_text(json.dumps({'agent': 0.8}))
    monkeypatch.setattr(platinum_governor, 'TRUST_FILE', trust_file)
    g = platinum_governor.PlatinumGovernor()
    assert g.check('agent', 0.7) is True
    assert g.check('agent', 0.9) is False


def test_log_action(tmp_path, monkeypatch):
    trust_file = tmp_path / 'trust.json'
    log_file = tmp_path / 'log.yaml'
    trust_file.write_text('{}')
    monkeypatch.setattr(platinum_governor, 'TRUST_FILE', trust_file)
    monkeypatch.setattr(platinum_governor, 'LOGBOOK_FILE', log_file)
    g = platinum_governor.PlatinumGovernor()
    g.log_action('escalation', {'foo': 'bar'})
    data = yaml.safe_load(log_file.read_text())
    assert isinstance(data, list)
    assert data and data[0]['action'] == 'escalation'


def test_update_trust_clamp(tmp_path, monkeypatch):
    trust_file = tmp_path / 'trust.json'
    monkeypatch.setattr(platinum_governor, 'TRUST_FILE', trust_file)
    g = platinum_governor.PlatinumGovernor()
    assert g.update_trust('a', 0.7) == 0.7
    assert g.update_trust('a', 0.5) == 1.0
    assert g.update_trust('a', -2.0) == 0.0


def test_escalation_integration(tmp_path, monkeypatch):
    trust_file = tmp_path / 'trust.json'
    log_file = tmp_path / 'log.yaml'
    monkeypatch.setattr(platinum_governor, 'TRUST_FILE', trust_file)
    monkeypatch.setattr(platinum_governor, 'LOGBOOK_FILE', log_file)
    governor = platinum_governor.PlatinumGovernor()
    monkeypatch.setattr(escalation_engine, 'behavior_audit', types.SimpleNamespace(log_action=lambda *a, **k: None))
    monkeypatch.setattr(escalation_engine, 'scene_status_tracker', types.SimpleNamespace(update_status=lambda *a, **k: None, get_status=lambda s: 'escalated'))
    monkeypatch.setattr(escalation_engine, 'memory_manager', types.SimpleNamespace(add_event=lambda *a, **k: None))
    monkeypatch.setattr(escalation_engine, 'GOVERNOR', governor)
    escalation_engine.escalate_scene('scene1', 'fail')
    data = yaml.safe_load(log_file.read_text())
    assert data and data[0]['scene'] == 'scene1'


def test_self_test(tmp_path, monkeypatch):
    trust_file = tmp_path / 'trust.json'
    log_file = tmp_path / 'log.yaml'
    trust_file.write_text(json.dumps({'a': 0.5}))
    log_file.write_text(yaml.safe_dump([]))
    spec = importlib.util.spec_from_file_location('platinum.self_test', os.path.join(os.path.dirname(__file__), '..', 'platinum', 'platinum_self_test.py'))
    self_test = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(self_test)
    monkeypatch.setattr(self_test, 'TRUST_FILE', trust_file, raising=False)
    monkeypatch.setattr(self_test, 'LOGBOOK_FILE', log_file, raising=False)
    assert self_test.run_tests() is True
