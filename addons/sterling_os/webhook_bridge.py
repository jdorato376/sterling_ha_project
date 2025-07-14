from flask import Flask, request
import requests
app = Flask(__name__)

@app.route('/sterling_webhook', methods=['POST'])
def incoming():
    payload = request.json
    text = payload.get("message", "(no message)")
    requests.post("http://localhost:5001/sterling/assistant", json={"query": text})
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(port=5006)
