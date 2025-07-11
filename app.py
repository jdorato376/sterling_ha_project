from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route("/sterling/health")
def health():
    return {"status": "ok"}

@app.route("/sterling/assistant", methods=["POST"])
def assistant():
    data = request.json
    return jsonify({
        "response": f"Received query: {data.get('query')}",
        "actions_taken": ["logged query"],
        "home_assistant_update": False,
        "cost_savings": "$0"
    })
@app.route("/etsy/orders", methods=["GET"])
def etsy_orders():
    return jsonify({
        "results": [  # <-- changed from "orders" to "results"
            {"id": "123", "status": "shipped", "item": "AI Smart Plug"},
            {"id": "124", "status": "processing", "item": "Smart Home Hub"}
        ]
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route("/webhook/homeassistant", methods=["POST"])
def homeassistant_webhook():
    data = request.json
    print(f"Received webhook from Home Assistant: {data}")
    return jsonify({"status": "received", "data": data}), 200
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook received:", data)
    return jsonify({"status": "received", "data": data}), 200

