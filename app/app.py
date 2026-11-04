"""Sample Flask application for ENSP461 Lab 1 - CI/CD with Jenkins."""
from flask import Flask, jsonify

app = Flask(__name__)

VERSION = "1.0.0"


@app.route("/")
def index():
    return jsonify(message="Hello from Meenakshi DevOps Lab", version=VERSION)


@app.route("/info")
def info():
    return jsonify(
        app="ensp461-lab1-sample-app",
        author="Meenakshi",
        version=VERSION,
        pipeline="Jenkins declarative CI/CD",
    )


@app.route("/health")
def health():
    return jsonify(status="UP"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
