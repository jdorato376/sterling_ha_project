import importlib.util
import os
import json

spec = importlib.util.spec_from_file_location('omni.synergy_tester', os.path.join(os.path.dirname(__file__), '..', 'omni', 'synergy_tester.py'))
synergy_tester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(synergy_tester)


def test_run_test(tmp_path, monkeypatch):
    registry = tmp_path / 'registry.json'
    monkeypatch.setattr(synergy_tester.agent_linker, 'LEDGER_FILE', registry, raising=False)
    result = synergy_tester.run_test()
    assert len(result) == 2

