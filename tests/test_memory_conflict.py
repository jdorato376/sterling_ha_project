import json
import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('runtime_engine', os.path.join(os.path.dirname(__file__), '..', 'runtime_engine.py'))
runtime_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_engine)

from json_store import JSONStoreError


def test_memory_conflict(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    monkeypatch.setattr(runtime_engine.runtime_memory.RUNTIME_STORE, 'path', mem)

    attempts = {'n': 0}
    real_write = runtime_engine.runtime_memory.JSONStore.write

    def flaky(self, data):
        attempts['n'] += 1
        if attempts['n'] < 4:
            raise JSONStoreError('fail')
        real_write(self, data)

    monkeypatch.setattr(runtime_engine.runtime_memory.JSONStore, 'write', flaky)

    runtime_engine.safe_write_memory({'foo': 'bar'})

    assert json.loads(mem.read_text()) == {}
    assert attempts['n'] >= 3
