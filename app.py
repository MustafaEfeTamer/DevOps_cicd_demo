from flask import Flask, Response
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

REQUESTS = Counter('request_count', 'Total Requests')

@app.route("/")
def home():
    REQUESTS.inc()
    return "Hello DevOps Demo"

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

app.run(host="0.0.0.0", port=5000)