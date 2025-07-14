import importlib.util
import os
import json

spec = importlib.util.spec_from_file_location('platinum.dominion_audit', os.path.join(os.path.dirname(__file__), '..', 'platinum', 'dominion_audit.py'))
dominion_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dominion_audit)


def test_run_audit(tmp_path, monkeypatch):
    audit_file = tmp_path / 'audit.json'
    monkeypatch.setattr(dominion_audit, 'AUDIT_FILE', audit_file)
    result = dominion_audit.run_audit()
    assert result['phase'] == '11'
    assert audit_file.exists()

