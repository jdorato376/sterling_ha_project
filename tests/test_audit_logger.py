import os
import sys
import json
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('audit_logger', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'audit_logger.py'))
audit_logger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_logger)


def test_log_event(tmp_path, monkeypatch):
    log_file = tmp_path / 'audit.json'
    monkeypatch.setattr(audit_logger, 'AUDIT_LOG', str(log_file))
    audit_logger.log_event('INFO', 'hello')
    data = log_file.read_text()
    assert 'hello' in data
    audit_logger.log_event('WARN', 'x')
    loaded = json.loads(log_file.read_text())
    assert len(loaded) == 2

