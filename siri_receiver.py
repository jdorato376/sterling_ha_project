"""Webhook receiver compatible with Siri/HomeKit."""

from flask import Blueprint, request, jsonify

siri_bp = Blueprint("siri_receiver", __name__)


@siri_bp.route("/siri/webhook", methods=["POST"])
def siri_webhook():
    data = request.get_json() or {}
    phrase = data.get("phrase", "")
    return jsonify({"received": phrase}), 200


__all__ = ["siri_bp"]
