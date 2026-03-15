from flask import Flask
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

REQUESTS = Counter('request_count', 'Total Requests')

@app.route("/")
def home():
    REQUESTS.inc()
    return "Hello DevOps Demo"

@app.route("/metrics")
def metrics():
    return generate_latest()

app.run(host="0.0.0.0", port=5000)