import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('addons.sterling_os.behavior_audit', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'behavior_audit.py'))
behavior_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(behavior_audit)


def test_log_and_verify(tmp_path, monkeypatch):
    audit = tmp_path / 'audit.jsonl'
    hash_file = audit.with_suffix('.sha256')
    monkeypatch.setattr(behavior_audit, 'AUDIT_FILE', audit)
    monkeypatch.setattr(behavior_audit, 'HASH_FILE', hash_file)
    behavior_audit.log_action('test', {'foo': 'bar'})
    lines = audit.read_text().splitlines()
    assert lines and 'test' in lines[0]
    assert behavior_audit.verify_hash() is True
