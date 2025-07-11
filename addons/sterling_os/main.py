from flask import Flask, jsonify, request
import json
from pathlib import Path

from . import memory_manager
from . import devgpt_engine
from . import intent_router
from . import fallback_router
from .autonomy_engine import AutonomyEngine
from . import timeline_orchestrator
from . import scene_executor

import sys
import os
import importlib.util
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, REPO_ROOT)
spec = importlib.util.spec_from_file_location('cognitive_router', os.path.join(REPO_ROOT, 'cognitive_router.py'))
cognitive_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cognitive_router)

app = Flask(__name__)

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config.json"
if CONFIG_PATH.exists():
    with CONFIG_PATH.open() as f:
        CONFIG = json.load(f)
else:
    CONFIG = {}

DEV_MODE = CONFIG.get("dev_mode", False)
MEMORY_ENABLED = CONFIG.get("memory_enabled", True)
ENABLE_DEVGPT = CONFIG.get("enable_devgpt", False)

if MEMORY_ENABLED:
    memory_manager.load_memory()

engine = AutonomyEngine()


def interpret_intent(intent: str) -> str:
    """Map intent strings to human-readable responses."""
    mapping = {
        "SterlingDailyBriefing": "Give me my daily briefing",
        "SterlingCheckGarage": "Is the garage door closed?",
        "SterlingRunScene": "Run the evening lights scene",
    }
    return mapping.get(intent, "I'm not sure how to help with that.")


@app.route("/sterling/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/sterling/assistant", methods=["POST"])
def sterling_assistant():
    """Route generic assistant queries through the intent router."""
    data = request.get_json(force=True)
    query = data.get("query") or data.get("phrase") or ""
    response = intent_router.route_intent(query)
    return jsonify({"response": response})


@app.route('/sterling/route', methods=['POST'])
def cognitive_route():
    """Route a query through the cognitive router."""
    data = request.get_json(force=True)
    query = data.get('query') or ''
    result = cognitive_router.handle_request(query)
    return jsonify(result)


@app.route('/ha-chat', methods=['POST'])
def ha_chat():
    token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    expected = os.environ.get('HA_TOKEN')
    if expected and token != expected:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True)
    query = data.get('message', '')
    result = cognitive_router.route_with_self_critique(query)
    return jsonify(result)


@app.route("/etsy/orders", methods=["GET"])
def etsy_orders():
    """Return an empty list of orders as a stub."""
    return jsonify({"results": []})


@app.route("/sterling/info", methods=["GET"])
def sterling_info():
    """Return basic version and status information."""
    return jsonify({
        "version": "1.0.0",
        "status": "ok"
    })


@app.route('/sterling/intent', methods=['POST'])
def handle_intent():
    """Return a response string for the provided intent or phrase."""
    data = request.get_json(force=True)
    phrase = data.get("phrase") or data.get("intent")
    response = intent_router.route_intent(phrase or "")
    return jsonify({"response": response})


@app.route('/sterling/contextual', methods=['POST'])
def contextual_intent():
    """Route phrases with memory-based fallback suggestions."""
    data = request.get_json(force=True)
    query = data.get("query") or ""
    response = intent_router.route_intent(query, fallback=True)
    return jsonify({"response": response})


@app.route('/sterling/fallback/query', methods=['POST'])
def fallback_query():
    """Return a response using Gemini with Ollama fallback."""
    data = request.get_json(force=True)
    prompt = data.get('query') or ''
    reply = fallback_router.route_query(prompt)
    return jsonify({'response': reply})


@app.route('/sterling/scene', methods=['POST'])
def run_scene():
    """Execute a named scene immediately."""
    data = request.get_json(force=True)
    name = data.get('name') or ''
    import asyncio
    result = asyncio.run(scene_executor.execute_scene(name))
    return jsonify({'success': result})


@app.route('/sterling/autonomy/start', methods=['POST'])
def autonomy_start():
    """Add a scene to the autonomy stack."""
    data = request.get_json(force=True)
    name = data.get('name') or ''
    engine.start_task(name)
    return jsonify({'queued': name})


@app.route('/sterling/autonomy/next', methods=['POST'])
def autonomy_next():
    """Run the next task in the autonomy engine."""
    import asyncio
    scene = asyncio.run(engine.run_next())
    return jsonify({'executed': scene})


@app.route('/sterling/intent/escalate', methods=['POST'])
def intent_escalate():
    """Placeholder route for escalation logic."""
    data = request.get_json(force=True)
    memory_manager.add_event(f"escalate:{data}")
    return jsonify({"status": "escalated"})


@app.route('/sterling/history', methods=['GET'])
def get_history():
    """Return stored event history from the memory manager."""
    return jsonify(memory_manager.load_memory())


@app.route('/sterling/timeline', methods=['GET'])
def get_timeline():
    """Return the memory timeline events."""
    return jsonify(memory_manager.get_timeline())


@app.route('/sterling/timeline/summary', methods=['GET'])
def get_timeline_summary():
    """Return a short summary of recent events."""
    summary = timeline_orchestrator.timeline_summary()
    return jsonify({'summary': summary})


@app.route('/sterling/failsafe/reset', methods=['POST'])
def failsafe_reset():
    """Reset memory and return safe mode status."""
    memory_manager.reset_memory()
    return jsonify({"status": "safe_mode", "message": "Sterling OS reset"})


if __name__ == "__main__":
    print("Sterling OS Add-on Running")
    if DEV_MODE and ENABLE_DEVGPT:
        devgpt_engine.run("startup", user_confirm=False, enabled=True)
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Sterling OS container stopped.")
