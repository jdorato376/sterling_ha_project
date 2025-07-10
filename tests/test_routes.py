import importlib.util
import os
import pytest

# Load the main module without requiring package installation
module_path = os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'main.py')
spec = importlib.util.spec_from_file_location('main', module_path)
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
    assert 'status' in res.get_json()

def test_sterling_assistant(client):
    payload = {'query': 'What is my schedule?', 'context': 'general'}
    res = client.post('/sterling/assistant', json=payload)
    assert res.status_code == 200
    assert 'response' in res.get_json()

def test_etsy_orders(client):
    res = client.get('/etsy/orders')
    assert res.status_code == 200
    assert 'results' in res.get_json()
