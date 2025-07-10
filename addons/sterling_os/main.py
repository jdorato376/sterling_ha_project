from flask import Flask, jsonify, request
import json
from pathlib import Path

from . import memory_manager
from . import devgpt_engine
from . import intent_router

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
    """Minimal placeholder assistant route."""
    _ = request.get_json(force=True)
    return jsonify({"response": "Assistant response placeholder"})


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
