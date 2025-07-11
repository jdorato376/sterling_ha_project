from flask import Flask, jsonify, request
import os
import platform
import subprocess
import datetime


app = Flask(__name__)
start_time = datetime.datetime.now()

@app.route("/")
def root():
    """Simple health check for container orchestration."""
    return jsonify(status="alive", version="4.0.0")

@app.route("/info")
def info():
    return jsonify({
        "models": ["gpt-4", "gpt-4o", "gpt-3.5"],
        "fallback_chain": "gpt-4 \u2192 gpt-4o \u2192 gpt-3.5",
        "commit": os.getenv("GITHUB_SHA", "local-dev"),
    })

@app.route("/metadata")
def metadata():
    """Return commit and runtime information."""
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        commit_date = subprocess.check_output(["git", "show", "-s", "--format=%cI", "HEAD"]).decode().strip()
    except Exception:
        commit = os.getenv("GITHUB_SHA", "unknown")
        commit_date = os.getenv("GITHUB_DATE", "unknown")
    return jsonify({
        "commit": commit,
        "commit_date": commit_date,
        "branch": os.getenv("GIT_BRANCH", "main"),
        "platform": platform.platform(),
    })

@app.route("/sterling/status", methods=["GET"])
def status():
    """Report runtime status and uptime information."""
    uptime = datetime.datetime.now() - start_time
    return jsonify({
        "status": "running",
        "uptime": str(uptime),
        "hostname": platform.node(),
        "containerized": os.environ.get("DOCKER_CONTAINER", "unknown"),
        "python_version": platform.python_version(),
    })

@app.route("/sterling/version", methods=["GET"])
def version():
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception as e:
        commit_hash = f"Error: {str(e)}"
    return jsonify({
        "commit_hash": commit_hash,
        "branch": os.getenv("GIT_BRANCH", "unknown"),
        "image_id": os.getenv("DOCKER_IMAGE", "unknown"),
    })

@app.route("/sterling/info", methods=["GET"])
def sterling_info():
    models = []
    try:
        import openai
        models.append("OpenAI")
    except ImportError:
        pass
    try:
        import ollama
        models.append("Ollama")
    except ImportError:
        pass
    return jsonify({
        "available_models": models,
        "fallback_chain": models[::-1] if models else ["None"],
    })

@app.route("/sterling/assistant", methods=["POST"])
def assistant():
    data = request.get_json(force=True)
    query = data.get("query", "")
    return jsonify({"response": "I'm not sure, but here's what I can try...", "query": query})

@app.route("/self-heal")
def heal():
    return jsonify(action="restart", status="initiated")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
