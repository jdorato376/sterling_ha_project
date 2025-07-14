import importlib.util
import os

spec = importlib.util.spec_from_file_location('threads.predictive_scheduler', os.path.join(os.path.dirname(__file__), '..', 'threads', 'predictive_scheduler.py'))
predictive_scheduler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predictive_scheduler)


def test_reprioritize(tmp_path, monkeypatch):
    reg = tmp_path / 'reg.json'
    reg.write_text('{"a": {"locked": false, "last_executed": "1"}, "b": {"locked": true, "last_executed": "0"}}')
    monkeypatch.setattr(predictive_scheduler, 'REGISTRY_FILE', reg)
    result = predictive_scheduler.reprioritize()
    assert result == ['a', 'b']
