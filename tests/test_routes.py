from dotenv import load_dotenv
import os
import requests

load_dotenv()

BASE_URL = "http://localhost:5000"
HEADERS = {"FLASK_API": os.getenv("FLASK_API")}

def test_health_check():
    res = requests.get(f"{BASE_URL}/sterling/health")
    assert res.status_code == 200
    assert "status" in res.json()

def test_sterling_assistant():
    payload = {"query": "What is my schedule?", "context": "general"}
    res = requests.post(f"{BASE_URL}/sterling/assistant", headers=HEADERS, json=payload)
    assert res.status_code == 200
    assert "response" in res.json()

def test_etsy_orders():
    res = requests.get(f"{BASE_URL}/etsy/orders", headers=HEADERS)
    assert res.status_code == 200
    assert "results" in res.json()
