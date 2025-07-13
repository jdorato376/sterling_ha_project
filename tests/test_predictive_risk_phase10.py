import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'predictive_risk',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'predictive_risk.py')
)
predictive_risk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predictive_risk)

spec2 = importlib.util.spec_from_file_location(
    'codex_diagnostics',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'codex_diagnostics.py')
)
codex_diagnostics = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(codex_diagnostics)


def test_evaluate_risk(tmp_path, monkeypatch):
    log = tmp_path / 'diag.json'
    monkeypatch.setattr(codex_diagnostics, 'DIAG_LOG', str(log))
    monkeypatch.setattr(predictive_risk, 'codex_diagnostics', codex_diagnostics)
    risks = predictive_risk.evaluate_risk({'a': 0.2}, 6, 0)
    assert 'low_weight:a' in risks
    data = log.read_text()
    assert 'low_weight:a' in data
