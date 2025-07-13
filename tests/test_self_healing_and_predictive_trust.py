import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'self_healing',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'self_healing.py')
)
self_healing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(self_healing)

spec2 = importlib.util.spec_from_file_location(
    'predictive_trust',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'predictive_trust.py')
)
predictive_trust = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(predictive_trust)


def test_trust_manager():
    predictive_trust.predictive_trust.record_success('a')
    predictive_trust.predictive_trust.record_success('a')
    predictive_trust.predictive_trust.record_failure('b')
    assert predictive_trust.predictive_trust.calculate_trust('a') > 0.8
    assert predictive_trust.predictive_trust.calculate_trust('b') < 0.5


def test_self_heal(monkeypatch):
    calls = {}

    def fake_update(agent, delta):
        calls['update'] = (agent, delta)

    def fake_classify(intent):
        return 'fallback_agent'

    def fake_escalate(scene, reason):
        calls['escalate'] = (scene, reason)
        return {}

    monkeypatch.setattr(self_healing.trust_registry, 'update_weight', fake_update)
    monkeypatch.setattr(self_healing.cognitive_router, 'classify_request', fake_classify)
    monkeypatch.setattr(self_healing.escalation_engine, 'escalate_scene', fake_escalate)
    monkeypatch.setattr(self_healing.scene_trace, 'record_scene_status', lambda *a, **k: None)

    msg = self_healing.self_heal('run', 'agent_x', 'oops')
    assert 'fallback_agent' in msg
    assert calls['update'][0] == 'agent_x'
    assert 'oops' in calls['escalate'][1]
