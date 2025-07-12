import importlib.util
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def _load(name, filename):
    full = f"addons.sterling_os.{name}"
    spec = importlib.util.spec_from_file_location(
        full,
        os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', filename),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


self_writing = _load('self_writing', 'self_writing.py')
agent_senate = _load('agent_senate', 'agent_senate.py')
risk_intelligence = _load('risk_intelligence', 'risk_intelligence.py')
patch_layer = _load('patch_layer', 'patch_layer.py')
command_stream = _load('command_stream', 'command_stream.py')
memory_manager = _load('memory_manager', 'memory_manager.py')


def test_infer_automation():
    yaml_out = self_writing.infer_automation(['motion detected'])
    assert 'motion_detected' in yaml_out


def test_agent_senate_majority():
    senate = agent_senate.AgentSenate(['a', 'b', 'c', 'd', 'e'])
    votes = {'a': True, 'b': True, 'c': False, 'd': True, 'e': False}
    assert senate.decide(votes, quorum=3)


def test_risk_detection():
    lines = ['ok', 'Error: bad']
    assert risk_intelligence.detect_risks(lines) == ['Error: bad']


def test_patch_layer():
    result = patch_layer.apply_patch('a: 1\n', {'b': 2})
    import yaml
    data = yaml.safe_load(result)
    assert data['b'] == 2


def test_command_stream(tmp_path, monkeypatch):
    file = tmp_path / 'memory.json'
    file.write_text('[]')
    monkeypatch.setattr(memory_manager.MEMORY_STORE, 'path', file)
    monkeypatch.setattr(command_stream.memory_manager.MEMORY_STORE, 'path', file)
    command_stream.record('reboot')
    data = json.loads(file.read_text())
    assert data[0]['event'] == 'cmd:reboot'
