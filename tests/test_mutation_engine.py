import importlib.util
import os
import json

MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'mutation', 'mutation_engine.py')

spec = importlib.util.spec_from_file_location('mutation.engine', MODULE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def test_mutate_agent(tmp_path, monkeypatch):
    reg = tmp_path / 'dna.json'
    reg.write_text('{}')
    monkeypatch.setattr(engine, 'REGISTRY_FILE', reg)
    engine.mutate_agent('agent', 'role')
    data = json.loads(reg.read_text())
    assert data['agent']['roles'] == ['role']
