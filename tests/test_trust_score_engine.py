import importlib.util
import os

spec = importlib.util.spec_from_file_location('risk.trust_score_engine', os.path.join(os.path.dirname(__file__), '..', 'risk', 'trust_score_engine.py'))
trust_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trust_engine)


def test_compute_score_bounds():
    m = {'success_rate': 0.8, 'escalation_frequency': 0.1, 'override_count': 1, 'failure_severity': 0.5}
    score = trust_engine.compute_score(m)
    assert 0 <= score <= 100
    assert round(score, 1) == score


def test_compute_score_clamped():
    assert trust_engine.compute_score({'success_rate': 0.0}) == 0.0
    assert trust_engine.compute_score({'success_rate': 1.5}) == 100.0
