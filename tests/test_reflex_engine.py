import importlib.util
import os
import sys
import types

MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'reflex', 'reflex_engine.py')


def load_module(monkeypatch):
    stub = types.ModuleType('escalation_engine')
    stub.escalate_scene = lambda scene, reason: {'scene': scene, 'reason': reason}
    monkeypatch.setitem(sys.modules, 'addons', types.ModuleType('addons'))
    monkeypatch.setitem(sys.modules, 'addons.sterling_os', types.ModuleType('sterling_os'))
    monkeypatch.setitem(sys.modules, 'addons.sterling_os.escalation_engine', stub)
    spec = importlib.util.spec_from_file_location('reflex.reflex_engine', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_monitor_event_triggers(monkeypatch):
    mod = load_module(monkeypatch)
    result = mod.monitor_event('scene', 120, 50)
    assert result['scene'] == 'scene'
    assert 'reason' in result


def test_monitor_event_ok(monkeypatch):
    mod = load_module(monkeypatch)
    monkeypatch.setattr(mod, 'load_shield', lambda: {})
    res = mod.monitor_event('scene', 10, 99)
    assert res['status'] == 'ok'
