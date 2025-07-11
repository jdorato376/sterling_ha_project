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
    assert res.get_json() == {"response": "I'm not sure, but here's what I can try..."}

def test_etsy_orders(client):
    res = client.get('/etsy/orders')
    assert res.status_code == 200
    assert res.get_json() == {"results": []}


def test_cognitive_route_endpoint(tmp_path, monkeypatch):
    mem_file = tmp_path / 'runtime_memory.json'
    mem_file.write_text('{}')

    spec = importlib.util.spec_from_file_location(
        'cognitive_router', os.path.join(os.path.dirname(__file__), '..', 'cognitive_router.py')
    )
    cognitive_router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cognitive_router)
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', mem_file)
    monkeypatch.setattr(main, 'cognitive_router', cognitive_router)

    with app.test_client() as cl:
        res = cl.post('/sterling/route', json={'query': 'show my budget'})
        assert res.status_code == 200
        assert res.get_json()['agent'] == 'finance'

    data = json.loads(mem_file.read_text())
    assert data['route_logs'][-1]['agent'] == 'finance'


def test_cognitive_route_escalation(tmp_path, monkeypatch):
    mem_file = tmp_path / 'runtime_memory.json'
    mem_file.write_text('{}')

    spec = importlib.util.spec_from_file_location(
        'cognitive_router', os.path.join(os.path.dirname(__file__), '..', 'cognitive_router.py')
    )
    cognitive_router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cognitive_router)
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', mem_file)
    monkeypatch.setattr(cognitive_router.agent_reflector.RUNTIME_STORE, 'path', mem_file)
    monkeypatch.setattr(main, 'cognitive_router', cognitive_router)

    with app.test_client() as cl:
        res = cl.post('/sterling/route', json={'query': 'toggle kitchen light'})
        assert res.status_code == 200
        body = res.get_json()
        assert body['agent'] == 'general'

    data = json.loads(mem_file.read_text())
    assert data['fallback_triggered'] is True


def test_sterling_info(client):
    res = client.get('/sterling/info')
    assert res.status_code == 200
    data = res.get_json()
    assert data["version"] == "1.0.0"
    assert data["status"] == "ok"


def test_handle_intent(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)
    payload = {"phrase": "SterlingCheckGarage"}
    res = client.post('/sterling/intent', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["response"] == "Is the garage door closed?"
    # memory file should record the intent
    timeline = json.loads(mem_file.read_text())
    assert timeline and timeline[-1]["event"].startswith("intent:")


def test_phrase_logging_and_timeline_filter(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)

    # Send a phrase that will be unknown
    payload = {"phrase": "Turn off the moon"}
    client.post('/sterling/intent', json=payload)

    timeline = json.loads(mem_file.read_text())
    # First event should log the phrase
    assert any(e["event"].startswith("phrase:") for e in timeline)

    # get_timeline filtering
    recent_unknown = main.memory_manager.get_timeline(limit=1, tag="unknown")
    assert recent_unknown and "unknown:" in recent_unknown[0]["event"]

    # recent phrases helper
    phrases = main.memory_manager.get_recent_phrases(limit=1)
    assert phrases and phrases[0]["event"].startswith("phrase:")


def test_get_history(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text('[{"timestamp": "2025-01-01T00:00:00Z", "event": "start"}]')

    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)
    with app.test_client() as cl:
        res = cl.get('/sterling/history')
        assert res.status_code == 200
        assert res.get_json()[0]["event"] == "start"
        assert "timestamp" in res.get_json()[0]


def test_failsafe_reset(tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text('[{"event": "x"}]')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)
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
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)
    with app.test_client() as cl:
        res = cl.get('/sterling/timeline')
        assert res.status_code == 200
        data = res.get_json()
        assert data[0]["event"] == "boot"


def test_contextual_fallback(client, tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)

    # First send a known intent so memory contains it
    client.post('/sterling/intent', json={"phrase": "SterlingCheckGarage"})

    # Now send a related free-form query
    res = client.post('/sterling/contextual', json={"query": "garage"})
    assert res.status_code == 200
    txt = res.get_json()["response"]
    assert "garage" in txt.lower()

    # fallback event should be logged
    timeline = json.loads(mem_file.read_text())
    assert any(e["event"].startswith("fallback:") for e in timeline)

    # verify get_recent_phrases contains the free-form query
    phrases = main.memory_manager.get_recent_phrases(limit=2, contains="garage")
    assert any("garage" in p["event"] for p in phrases)


def test_ollama_fallback_logging(tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)

    class DummyOllama:
        @staticmethod
        def generate(model, prompt):
            return {"response": "local hello"}

    monkeypatch.setitem(sys.modules, "ollama", DummyOllama)

    with app.test_client() as cl:
        res = cl.post('/sterling/contextual', json={"query": "nonsense"})
        assert res.status_code == 200
        assert res.get_json()["response"] == "local hello"

    events = json.loads(mem_file.read_text())
    assert any(e["event"].startswith("_ollama_fallback:") for e in events)
    assert any(e["event"].startswith("_local_llm_response:local hello") for e in events)


def test_contextual_suggestion(monkeypatch, tmp_path):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)

    main.memory_manager.add_event("phrase:SterlingCheckGarage")
    main.memory_manager.add_event("intent:SterlingCheckGarage")

    suggestion = main.intent_router.contextual_suggestion("garage")
    assert suggestion and "garage" in suggestion.lower()


def test_agent_fallback_chain(monkeypatch, tmp_path):
    from addons.sterling_os import agent_orchestrator

    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(agent_orchestrator.memory_manager.MEMORY_STORE, "path", mem_file)
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)

    monkeypatch.setattr(agent_orchestrator, "_gemini_response", lambda q: (_ for _ in ()).throw(RuntimeError("fail")))

    def fake_local(prompt):
        agent_orchestrator.memory_manager.add_event(f"_ollama_fallback:{prompt}")
        agent_orchestrator.memory_manager.add_event("_local_llm_response:local hi")
        return "local hi"

    monkeypatch.setattr(agent_orchestrator, "_local_llm_response", fake_local)

    result = agent_orchestrator.handle_query("hello")
    assert result["agent_used"] == "ollama"
    assert result["response"] == "local hi"

    events = json.loads(mem_file.read_text())
    assert any(e["event"].startswith("_ollama_fallback:") for e in events)


def test_get_timeline_multiple_tags(tmp_path, monkeypatch):
    mem_file = tmp_path / "memory_timeline.json"
    mem_file.write_text("[]")
    monkeypatch.setattr(main.memory_manager.MEMORY_STORE, "path", mem_file)

    main.memory_manager.add_event("fallback:one")
    main.memory_manager.add_event("_ollama_fallback:two")

    events = main.memory_manager.get_timeline(tags=["fallback", "_ollama_fallback"])
    assert len(events) == 2


def test_ha_chat_endpoint(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        'cognitive_router', os.path.join(os.path.dirname(__file__), '..', 'cognitive_router.py')
    )
    cognitive_router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cognitive_router)

    monkeypatch.setattr(os, 'environ', {**os.environ, 'HA_TOKEN': 'token'})

    with app.test_client() as cl:
        res = cl.post('/ha-chat', json={'message': 'hello'}, headers={'Authorization': 'Bearer token'})
        assert res.status_code == 200

