import asyncio
import json
import importlib.util
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

# Import modules directly
spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.autonomy_engine',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'autonomy_engine.py'))
autonomy_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(autonomy_engine)

spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.scene_executor',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'scene_executor.py'))
scene_executor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene_executor)

spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.fallback_router',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'fallback_router.py'))
fallback_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback_router)

spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.timeline_orchestrator',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'timeline_orchestrator.py'))
timeline_orchestrator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timeline_orchestrator)

spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.memory_manager',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'memory_manager.py'))
memory_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_manager)


@pytest.fixture(autouse=True)
def temp_memory(tmp_path, monkeypatch):
    file = tmp_path / 'memory.json'
    file.write_text('[]')
    monkeypatch.setattr(memory_manager.MEMORY_STORE, 'path', file)
    monkeypatch.setattr(autonomy_engine.memory_manager.MEMORY_STORE, 'path', file)
    monkeypatch.setattr(scene_executor.memory_manager.MEMORY_STORE, 'path', file)
    monkeypatch.setattr(fallback_router.memory_manager.MEMORY_STORE, 'path', file)
    monkeypatch.setattr(timeline_orchestrator.memory_manager.MEMORY_STORE, 'path', file)
    yield


def test_fallback_router(monkeypatch):
    events = []
    monkeypatch.setattr(fallback_router.memory_manager, 'add_event', lambda e: events.append(e))
    monkeypatch.setattr(fallback_router, '_gemini_request', lambda p: (_ for _ in ()).throw(RuntimeError()))
    monkeypatch.setattr(fallback_router, '_ollama_request', lambda p: 'local')
    assert fallback_router.route_query('hello') == 'local'
    assert events and events[-1] == '_ollama_fallback:hello'


def test_scene_executor(monkeypatch, tmp_path):
    mapping = {'evening': 'scene.evening'}
    map_file = tmp_path / 'map.json'
    map_file.write_text(json.dumps(mapping))
    monkeypatch.setenv('SCENE_MAP_PATH', str(map_file))
    monkeypatch.setattr(scene_executor, 'SCENE_MAP_PATH', str(map_file))
    monkeypatch.setenv('HOME_ASSISTANT_URL', 'http://example.local')
    monkeypatch.setattr(scene_executor, 'HOME_ASSISTANT_URL', 'http://example.local')
    called = {}

    class DummyResponse:
        def __init__(self):
            self.status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def raise_for_status(self):
            called['hit'] = True

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def post(self, *args, **kwargs):
            return DummyResponse()

    monkeypatch.setattr(scene_executor.aiohttp, 'ClientSession', lambda: DummySession())
    monkeypatch.setattr(scene_executor.memory_manager, 'add_event', lambda e: called.setdefault('event', e))
    result = asyncio.run(scene_executor.execute_scene('evening'))
    assert result is True
    assert called.get('event') == 'scene:evening'


def test_timeline_prune(monkeypatch, tmp_path):
    now = datetime.now(timezone.utc)
    data = [
        {'timestamp': (now - timedelta(days=2)).isoformat(), 'event': 'old'},
        {'timestamp': now.isoformat(), 'event': 'new'},
    ]
    file = tmp_path / 'memory.json'
    file.write_text(json.dumps(data))
    monkeypatch.setattr(timeline_orchestrator.memory_manager.MEMORY_STORE, 'path', file)
    remaining = timeline_orchestrator.prune_older_than(1)
    assert len(remaining) == 1
    assert remaining[0]['event'] == 'new'


def test_autonomy_engine(monkeypatch):
    engine = autonomy_engine.AutonomyEngine()
    events = []
    monkeypatch.setattr(autonomy_engine.memory_manager, 'add_event', lambda e: events.append(e))
    async def fake_exec(name):
        events.append(f'exec:{name}')
        return True
    monkeypatch.setattr(autonomy_engine.scene_executor, 'execute_scene', fake_exec)
    engine.start_task('evening')
    engine.interrupt_task('urgent')
    asyncio.run(engine.run_next())
    assert 'exec:urgent' in events
