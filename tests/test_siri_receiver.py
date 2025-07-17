from flask import Flask
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from siri_receiver import siri_bp


def test_siri_webhook():
    app = Flask(__name__)
    app.register_blueprint(siri_bp)
    client = app.test_client()
    res = client.post('/siri/webhook', json={'phrase': 'lights on'})
    assert res.status_code == 200
    assert res.get_json()['received'] == 'lights on'
