import os
import sys
import importlib.util
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'routine_engine',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'routine_engine.py')
)
routine_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routine_engine)

import types


def test_routine_triggers(monkeypatch):
    scene_executor = types.ModuleType('addons.sterling_os.scene_executor')
    memory_manager = types.ModuleType('addons.sterling_os.memory_manager')
    monkeypatch.setitem(sys.modules, 'addons', types.ModuleType('addons'))
    monkeypatch.setitem(sys.modules, 'addons.sterling_os', types.ModuleType('addons.sterling_os'))
    monkeypatch.setitem(sys.modules, 'addons.sterling_os.scene_executor', scene_executor)
    monkeypatch.setitem(sys.modules, 'addons.sterling_os.memory_manager', memory_manager)
    called = {}
    monkeypatch.setattr(scene_executor, 'execute_scene', lambda n: called.setdefault('scene', n), raising=False)
    monkeypatch.setattr(memory_manager, 'add_event', lambda e: called.setdefault('event', e), raising=False)

    dt = datetime(2025, 1, 1, 7)  # Wednesday morning
    states = {'bedroom_lights': 'on', 'watch_active': True}

    result = routine_engine.evaluate_routines(now=dt, states=states)
    assert result == 'MorningOpsScene'
    assert called.get('scene') == 'MorningOpsScene'
    assert called.get('event') == 'routine:MorningOpsScene'
