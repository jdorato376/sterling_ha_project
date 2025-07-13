import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('addons.sterling_os.escalation_engine', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'escalation_engine.py'))
escalation_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(escalation_engine)

spec = importlib.util.spec_from_file_location('addons.sterling_os.scene_status_tracker', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'scene_status_tracker.py'))
scene_status_tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene_status_tracker)

spec = importlib.util.spec_from_file_location('addons.sterling_os.behavior_audit', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'behavior_audit.py'))
behavior_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(behavior_audit)


def test_escalate_scene(tmp_path, monkeypatch):
    audit = tmp_path / 'audit.jsonl'
    hash_file = audit.with_suffix('.sha256')
    status = tmp_path / 'status.json'
    monkeypatch.setattr(escalation_engine.behavior_audit, 'AUDIT_FILE', audit)
    monkeypatch.setattr(escalation_engine.behavior_audit, 'HASH_FILE', hash_file)
    monkeypatch.setattr(escalation_engine.scene_status_tracker, '_STATUS_STORE', scene_status_tracker.JSONStore(status, default={}))
    result = escalation_engine.escalate_scene('scene1', 'fail')
    assert escalation_engine.scene_status_tracker.get_status('scene1') == 'escalated'
    lines = audit.read_text().splitlines()
    assert lines and 'scene1' in lines[0]
    assert escalation_engine.behavior_audit.verify_hash()
