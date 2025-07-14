import importlib.util
import os
import json

MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'concord', 'concord_agent.py')

spec = importlib.util.spec_from_file_location('concord.concord_agent', MODULE_PATH)
concord = importlib.util.module_from_spec(spec)
spec.loader.exec_module(concord)


def test_record_grade(tmp_path, monkeypatch):
    grade_file = tmp_path / 'grade.json'
    monkeypatch.setattr(concord, 'GRADEBOOK_FILE', grade_file)
    winner = concord.record_grade('p1', {'a': 90, 'b': 80})
    assert winner == 'a'
    data = json.loads(grade_file.read_text())
    assert data and data[0]['winner'] == 'a'
