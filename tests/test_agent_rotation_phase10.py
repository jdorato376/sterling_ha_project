import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'agent_rotation',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'agent_rotation.py')
)
agent_rotation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_rotation)

spec2 = importlib.util.spec_from_file_location(
    'trust_registry',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'trust_registry.py')
)
trust_registry = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(trust_registry)


def test_record_and_rotate(tmp_path, monkeypatch):
    card = tmp_path / 'score.json'
    monkeypatch.setattr(agent_rotation, 'SCORECARD_FILE', str(card))
    monkeypatch.setattr(agent_rotation.trust_registry, 'update_weight', lambda a, d: None)
    monkeypatch.setattr(agent_rotation.trust_registry, 'load_weights', lambda: {'a': 0.5, 'b': 0.9})
    for i in range(10):
        agent_rotation.record_result('a', success=(i % 4 == 0))
    assert agent_rotation.should_rotate('a') is True
    alt = agent_rotation.rotate_agent('a')
    assert alt == 'b'
    data = json.loads(card.read_text())
    assert 'a' in data
