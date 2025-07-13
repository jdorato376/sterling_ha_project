import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('scene_trace', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'scene_trace.py'))
scene_trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene_trace)


def test_record_scene(tmp_path, monkeypatch):
    trace_file = tmp_path / 'trace.json'
    monkeypatch.setattr(scene_trace, 'TRACE_FILE', trace_file)
    entry = scene_trace.record_scene_status('s1', 'done', ['a'], 0.9)
    data = json.loads(trace_file.read_text())
    assert data[0]['scene'] == 's1'
    assert entry['quorum_score'] == 0.9

