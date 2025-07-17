import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_self_heal(tmp_path, monkeypatch):
    log = tmp_path / 'diagnostics_log.json'
    log.write_text('[{"risks": ["Error: config corrupted"]}]')
    backup_dir = tmp_path / 'backups'
    backup_dir.mkdir()
    target = tmp_path / 'config.yaml'
    target.write_text('bad')
    (backup_dir / 'config.yaml').write_text('good')

    import self_repair
    monkeypatch.setattr(self_repair, 'DIAG_LOG', log)
    monkeypatch.setattr(self_repair, 'BACKUP_DIR', backup_dir)

    assert self_repair.self_heal(target)
    assert target.read_text() == 'good'
