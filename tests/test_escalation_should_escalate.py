import os
import sys
import json
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec_c = importlib.util.spec_from_file_location('addons.sterling_os.agent_constitution', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'agent_constitution.py'))
agent_constitution = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(agent_constitution)

spec_e = importlib.util.spec_from_file_location('addons.sterling_os.escalation_engine', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'escalation_engine.py'))
escalation_engine = importlib.util.module_from_spec(spec_e)
spec_e.loader.exec_module(escalation_engine)
escalation_engine.agent_constitution = agent_constitution


def test_should_escalate(tmp_path, monkeypatch):
    const_file = tmp_path / 'c.json'
    const_file.write_text(json.dumps({
        'agents': {'a': {}},
        'escalation_protocols': {'uncertainty_threshold': 0.3}
    }))
    monkeypatch.setattr(agent_constitution, 'CONSTITUTION_FILE', const_file)
    monkeypatch.setattr(agent_constitution, '_load', lambda: json.loads(const_file.read_text()))
    res1 = escalation_engine.should_escalate(0.2, 0.6)
    assert res1 is True
    res2 = escalation_engine.should_escalate(0.9, 0.4)
    assert res2 is True
    res3 = escalation_engine.should_escalate(0.9, 0.8)
    assert res3 is False
