import importlib.util
import os
import pytest
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Load the main module without requiring package installation
module_path = os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'main.py')
spec = importlib.util.spec_from_file_location('addons.sterling_os.main', module_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app

@pytest.fixture

def client():
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get('/sterling/health')
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}

def test_sterling_assistant(client):
    payload = {'query': 'What is my schedule?', 'context': 'general'}
    res = client.post('/sterling/assistant', json=payload)
    assert res.status_code == 200
    assert res.get_json() == {"response": "Assistant response placeholder"}

def test_etsy_orders(client):
    res = client.get('/etsy/orders')
    assert res.status_code == 200
    assert res.get_json() == {"results": []}


def test_sterling_info(client):
    res = client.get('/sterling/info')
    assert res.status_code == 200
    data = res.get_json()
    assert data["version"] == "1.0.0"
    assert data["status"] == "ok"


def test_handle_intent(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager, "MEMORY_FILE", mem_file)
    payload = {"phrase": "SterlingCheckGarage"}
    res = client.post('/sterling/intent', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["response"] == "Is the garage door closed?"
    # memory file should record the intent
    timeline = json.loads(mem_file.read_text())
    assert timeline and timeline[-1]["event"].startswith("intent:")


def test_get_history(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text('[{"timestamp": "2025-01-01T00:00:00Z", "event": "start"}]')

    monkeypatch.setattr(main.memory_manager, "MEMORY_FILE", mem_file)
    with app.test_client() as cl:
        res = cl.get('/sterling/history')
        assert res.status_code == 200
        assert res.get_json()[0]["event"] == "start"
        assert "timestamp" in res.get_json()[0]


def test_failsafe_reset(tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text('[{"event": "x"}]')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main.memory_manager, "MEMORY_FILE", mem_file)
    with app.test_client() as cl:
        res = cl.post('/sterling/failsafe/reset')
        assert res.status_code == 200
        assert res.get_json()["status"] == "safe_mode"
        # memory file should be emptied
        data = json.loads(mem_file.read_text())
        assert data == []


def test_get_timeline(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text('[{"timestamp": "2025-01-01T00:00:00Z", "event": "boot"}]')
    monkeypatch.setattr(main.memory_manager, "MEMORY_FILE", mem_file)
    with app.test_client() as cl:
        res = cl.get('/sterling/timeline')
        assert res.status_code == 200
        data = res.get_json()
        assert data[0]["event"] == "boot"
