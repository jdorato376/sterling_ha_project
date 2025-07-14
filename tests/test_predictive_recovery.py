import os
import sys
import json
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'addons.sterling_os.predictive_recovery',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'predictive_recovery.py')
)
predictive_recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predictive_recovery)


def test_checkpoint_save_and_load(tmp_path, monkeypatch):
    file = tmp_path / '.codex_recovery.json'
    monkeypatch.setattr(predictive_recovery, 'RECOVERY_LOG', str(file))
    predictive_recovery.save_checkpoint('scene_a', {'state': 'active'})
    result = predictive_recovery.get_last_checkpoint('scene_a')
    assert result['scene_id'] == 'scene_a'
    assert result['data']['state'] == 'active'


def test_checkpoint_limit(tmp_path, monkeypatch):
    file = tmp_path / '.codex_recovery.json'
    monkeypatch.setattr(predictive_recovery, 'RECOVERY_LOG', str(file))
    for i in range(predictive_recovery.MAX_CHECKPOINTS + 5):
        predictive_recovery.save_checkpoint(str(i), {'n': i})
    data = json.loads(file.read_text())
    assert len(data) == predictive_recovery.MAX_CHECKPOINTS
    last = predictive_recovery.get_last_checkpoint(str(predictive_recovery.MAX_CHECKPOINTS - 1))
    assert last['scene_id'] == str(predictive_recovery.MAX_CHECKPOINTS - 1)
