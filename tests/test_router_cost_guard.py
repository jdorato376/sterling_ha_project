import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import router_cost_guard


def test_route_budget(monkeypatch):
    def fake_route_query(query):
        return {"model": "premium", "cost": 0.1, "response": "hi"}
    def fake_estimate(model_key, i, o):
        return 0.2
    monkeypatch.setattr(router_cost_guard, 'route_query', fake_route_query)
    monkeypatch.setattr(router_cost_guard, 'estimate_cost', fake_estimate)
    result = router_cost_guard.route_with_budget('hello', budget=0.05)
    assert result['model'] == 'free'
    assert result['cost'] == 0.0
