import os
import logging
from flask import Flask, request, jsonify
from routing_logic import route_query

app = Flask(__name__)

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = os.environ.get("REGION", "us-central1")


@app.route("/route", methods=["POST"])
def handle_routing():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    query = request.json.get("query")
    if not query:
        return jsonify({"error": "Query missing"}), 400

    try:
        result = route_query(query, project_id=GCP_PROJECT_ID)
        return jsonify(result), 200
    except Exception as e:  # pragma: no cover - runtime safeguard
        logging.exception("Routing error")
        return jsonify({"error": "An internal error has occurred."}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
