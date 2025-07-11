import json
import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('runtime_engine', os.path.join(os.path.dirname(__file__), '..', 'runtime_engine.py'))
runtime_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_engine)

spec = importlib.util.spec_from_file_location('git_diff_analyzer', os.path.join(os.path.dirname(__file__), '..', 'git_diff_analyzer.py'))
git_diff_analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_diff_analyzer)


def test_update_runtime_config(tmp_path, monkeypatch):
    runtime_file = tmp_path / 'runtime_memory.json'
    monkeypatch.setattr(runtime_engine.RUNTIME_STORE, 'path', runtime_file)
    monkeypatch.setattr(git_diff_analyzer, 'get_last_commit_diff', lambda: {'modified': ['app.py']})
    monkeypatch.setattr(runtime_engine, 'get_last_commit_diff', git_diff_analyzer.get_last_commit_diff)
    runtime_engine.update_runtime_config()
    data = json.loads(runtime_file.read_text())
    assert data['monitor_frequency_sec'] == 10

