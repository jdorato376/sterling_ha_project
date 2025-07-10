from flask import Flask, jsonify, request

app = Flask(__name__)


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


if __name__ == "__main__":
    print("Sterling OS Add-on Running")
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Sterling OS container stopped.")
