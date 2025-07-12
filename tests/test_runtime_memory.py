import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import runtime_memory


def test_read_invalid_resets(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    mem.write_text('{"bad": 1}')
    monkeypatch.setattr(runtime_memory.RUNTIME_STORE, 'path', mem)
    data = runtime_memory.read_memory()
    assert data == {}
    # backup file created
    assert mem.with_suffix('.bak').exists()


def test_write_invalid(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    monkeypatch.setattr(runtime_memory.RUNTIME_STORE, 'path', mem)
    runtime_memory.write_memory({'bad': 2})
    # file should not be created due to invalid schema
    assert not mem.exists()
    # backup of invalid data should exist
    assert mem.with_suffix('.bak').exists()


def test_health_check(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    mem.write_text('{}')
    monkeypatch.setattr(runtime_memory.RUNTIME_STORE, 'path', mem)
    # should not raise
    runtime_memory.run_health_check()


def test_health_check_failure(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    monkeypatch.setattr(runtime_memory.RUNTIME_STORE, 'path', mem)
    with pytest.raises(RuntimeError):
        runtime_memory.run_health_check()
