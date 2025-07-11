import os
import subprocess
import datetime
import platform

start_time = datetime.datetime.now()

@app.route("/sterling/status", methods=["GET"])
def status():
    uptime = datetime.datetime.now() - start_time
    return jsonify({
        "status": "running",
        "uptime": str(uptime),
        "hostname": platform.node(),
        "containerized": os.environ.get("DOCKER_CONTAINER", "unknown"),
        "python_version": platform.python_version()
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
        "image_id": os.getenv("DOCKER_IMAGE", "unknown")
    })

@app.route("/sterling/info", methods=["GET"])
def info():
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
        "fallback_chain": models[::-1] if models else ["None"]
    })

