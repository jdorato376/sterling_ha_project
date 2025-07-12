import os
import sys
import importlib.util
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'scene_delta_tracker',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'scene_delta_tracker.py')
)
scene_delta_tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene_delta_tracker)


def test_update_delta(tmp_path, monkeypatch):
    current = tmp_path / 'current.json'
    expected = tmp_path / 'expected.json'
    delta_log = tmp_path / 'delta.yaml'
    current.write_text(json.dumps({'lights': 'on'}))
    expected.write_text(json.dumps({'lights': 'off'}))

    monkeypatch.setattr(scene_delta_tracker, 'CURRENT_STATE_FILE', current)
    monkeypatch.setattr(scene_delta_tracker, 'EXPECTED_MODEL_FILE', expected)
    monkeypatch.setattr(scene_delta_tracker, 'DELTA_LOG_FILE', delta_log)

    delta = scene_delta_tracker.update_delta()
    assert delta['lights']['current'] == 'on'
    assert delta['lights']['expected'] == 'off'
    assert delta_log.exists()
