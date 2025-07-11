import json
import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('schema_escalator', os.path.join(os.path.dirname(__file__), '..', 'schema_escalator.py'))
schema_escalator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema_escalator)


def test_no_schema_returns_true(tmp_path, monkeypatch):
    path = tmp_path / 'schema.json'
    path.write_text('{}')
    monkeypatch.setattr(schema_escalator.SCHEMA_STORE, 'path', path)
    assert schema_escalator.check_schema('unknown', {'foo': 'bar'}) is True


def test_missing_key_fails(tmp_path, monkeypatch):
    path = tmp_path / 'schema.json'
    schema = {'finance': {'expected_keys': ['response']}}
    path.write_text(json.dumps(schema))
    monkeypatch.setattr(schema_escalator.SCHEMA_STORE, 'path', path)
    assert schema_escalator.check_schema('finance', {}) is False


def test_success_value(tmp_path, monkeypatch):
    path = tmp_path / 'schema.json'
    schema = {'home': {'expected_keys': ['status'], 'success_value': 'ok'}}
    path.write_text(json.dumps(schema))
    monkeypatch.setattr(schema_escalator.SCHEMA_STORE, 'path', path)
    assert schema_escalator.check_schema('home', {'status': 'ok'}) is True
    assert schema_escalator.check_schema('home', {'status': 'fail'}) is False

