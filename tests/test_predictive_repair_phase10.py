import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'predictive_repair',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'predictive_repair.py')
)
predictive_repair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predictive_repair)


def test_analyze_metrics():
    score = predictive_repair.analyze_metrics(0.9, 0.9, 0.2, 0.1)
    assert score > 0.25


def test_predictive_repair(tmp_path, monkeypatch):
    log = tmp_path / 'repairs.json'
    monkeypatch.setattr(predictive_repair, 'REPAIR_LOG', str(log))
    res = predictive_repair.predictive_repair(0.9, 0.9, 0.9, 0.9)
    assert res['action'] == 'repair'
    data = json.loads(log.read_text())
    assert data
