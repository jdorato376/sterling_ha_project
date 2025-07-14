from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms_webhook():
    body = request.form['Body']
    requests.post("http://localhost:5001/sterling/assistant", json={"query": body})
    return "OK"

if __name__ == '__main__':
    app.run(port=5005)
