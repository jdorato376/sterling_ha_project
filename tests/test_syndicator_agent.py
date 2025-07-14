import importlib.util
import os
import json
import yaml

MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'syndication', 'syndicator_agent.py')


def load_module():
    spec = importlib.util.spec_from_file_location('syndication.syndicator_agent', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_predict_next(tmp_path, monkeypatch):
    mod = load_module()
    f = tmp_path / 'clusters.json'
    f.write_text('[{"predicted_next": "test"}]')
    monkeypatch.setattr(mod, 'CLUSTER_FILE', f)
    assert mod.predict_next() == 'test'


def test_select_model(tmp_path, monkeypatch):
    mod = load_module()
    router = tmp_path / 'router.yaml'
    router.write_text('route_policies:\n  priority: [m1]\ncost_threshold:\n  max_cost: 0.0')
    trust = tmp_path / 'trust.json'
    trust.write_text('{"m1": {"trust": 90, "cost": 0.0}}')
    monkeypatch.setattr(mod, 'ROUTER_FILE', router)
    monkeypatch.setattr(mod, 'TRUST_FILE', trust)
    assert mod.select_model() == 'm1'
