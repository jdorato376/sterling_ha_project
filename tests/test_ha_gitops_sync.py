import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('addons.sterling_os.ha_gitops_sync', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'ha_gitops_sync.py'))
ha_gitops_sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ha_gitops_sync)
spec_a = importlib.util.spec_from_file_location('audit_logger', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'audit_logger.py'))
audit_logger = importlib.util.module_from_spec(spec_a)
spec_a.loader.exec_module(audit_logger)
ha_gitops_sync.log_event = audit_logger.log_event


def test_validate_yaml(tmp_path):
    good = tmp_path / 'good.yaml'
    good.write_text('a: 1\n')
    bad = tmp_path / 'bad.yaml'
    bad.write_text('a: [1,\n')
    log = tmp_path / 'audit.json'
    ha_gitops_sync.log_event = lambda *a, **k: None
    assert ha_gitops_sync.validate_yaml(str(good)) is True
    assert ha_gitops_sync.validate_yaml(str(bad)) is False
