import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.smart_router',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'smart_router.py')
)
smart_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smart_router)


def test_router_selection(monkeypatch):
    monkeypatch.setattr(smart_router, 'trust_registry', {'a': 0.9, 'b': 0.2})
    monkeypatch.setattr(smart_router, 'AGENT_MAP', {'a': '', 'b': ''})
    monkeypatch.setattr(smart_router, 'send_to_agent', lambda a, i, c: {'agent': a})
    res = smart_router.smart_route('on', 'ctx')
    assert res['agent'] == 'a'


def test_router_fallback(monkeypatch):
    monkeypatch.setattr(smart_router, 'trust_registry', {'a': 0.4})
    monkeypatch.setattr(smart_router, 'AGENT_MAP', {'a': ''})
    monkeypatch.setattr(smart_router, 'send_to_agent', lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError()))
    monkeypatch.setattr(smart_router, 'fallback_to_safe_mode', lambda i: {'agent': 'fallback'})
    res = smart_router.smart_route('x', 'ctx')
    assert res['agent'] == 'fallback'
