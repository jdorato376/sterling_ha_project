import importlib.util
import os
import json
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app


@pytest.fixture
def client():
    os.environ['HEARTBEAT_INTERVAL'] = '0'
    with app.test_client() as client:
        yield client


def test_heartbeat_basic(client):
    res = client.get('/heartbeat')
    assert res.status_code == 200
    data = res.get_json()
    assert 'timestamp' in data
    assert 'uptime' in data
    assert data['version'] == os.getenv('APP_VERSION', '4.0.0')


def test_heartbeat_verbose(client):
    res = client.get('/heartbeat?verbose=true')
    assert res.status_code == 200
    data = res.get_json()
    assert 'last_restart' in data
    assert 'memory_sync' in data


def test_restart_updates_uptime(tmp_path, monkeypatch):
    hb_file = tmp_path / 'uptime.json'
    monkeypatch.setattr(app_module.uptime_tracker, 'STATE_FILE', hb_file)
    app_module.uptime_tracker.record_start()
    first = json.loads(hb_file.read_text())['time_started']
    # simulate restart
    app_module.uptime_tracker.record_start()
    data = json.loads(hb_file.read_text())
    assert data['time_restarted'] is not None
    assert data['time_started'] == first



