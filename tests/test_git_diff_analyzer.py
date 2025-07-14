import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('git_diff_analyzer', os.path.join(os.path.dirname(__file__), '..', 'git_diff_analyzer.py'))
git_diff_analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_diff_analyzer)


def test_parse_git_diff(monkeypatch):
    sample = '+++ b/app.py\n+print("hi")\n-removed'
    def fake_check_output(cmd, stderr=None):
        return sample.encode()
    monkeypatch.setattr(git_diff_analyzer.subprocess, 'check_output', fake_check_output)
    result = git_diff_analyzer.get_last_commit_diff()
    assert 'modified' in result
    assert 'app.py' in result['modified']

