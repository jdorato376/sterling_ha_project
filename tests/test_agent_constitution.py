import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'agent_constitution',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'agent_constitution.py')
)
agent_constitution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_constitution)


def test_constitution_rules(tmp_path, monkeypatch):
    f = tmp_path / 'constitution.json'
    f.write_text(json.dumps({
        'agentA': {
            'allowed': ['read'],
            'escalate': ['write'],
            'can_override': ['agentB'],
            'cannot_override': []
        }
    }))
    monkeypatch.setattr(agent_constitution, 'CONSTITUTION_FILE', f)

    assert agent_constitution.can_act('agentA', 'read') is True
    assert agent_constitution.can_act('agentA', 'write') is False
    assert agent_constitution.requires_escalation('agentA', 'write') is True
    assert agent_constitution.can_override('agentA', 'agentB') is True
    assert agent_constitution.can_override('agentA', 'agentC') is False
