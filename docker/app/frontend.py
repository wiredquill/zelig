import json
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

# Load configuration from log_messages.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../configs/log_messages.json')
with open(CONFIG_FILE, 'r') as f:
    pod_config = json.load(f)

# Dictionary to hold the current state of each pod
pods_state = {pod_name: {"status": "running", "http_mode": "200 OK"} for pod_name in pod_config.keys()}


@app.route('/')
def index():
    """
    Render the main page displaying all pods, their states, and controls.
    """
    return render_template('index.html', pods=pods_state, config=pod_config)


@app.route('/set_mode/<pod_name>/<mode>', methods=['POST'])
def set_mode(pod_name, mode):
    """
    Set the mode of a specific pod.
    Modes:
        - running: Pod responds with 200 OK
        - error: Pod responds with 500 Internal Server Error
        - dead: Pod does not respond
    """
    if pod_name in pods_state:
        if mode == "running":
            pods_state[pod_name]["status"] = "running"
            pods_state[pod_name]["http_mode"] = "200 OK"
        elif mode == "error":
            pods_state[pod_name]["status"] = "error"
            pods_state[pod_name]["http_mode"] = "500 Internal Server Error"
        elif mode == "dead":
            pods_state[pod_name]["status"] = "dead"
            pods_state[pod_name]["http_mode"] = "No Response"
        else:
            return jsonify({"error": "Invalid mode"}), 400
        return jsonify({"message": f"Mode of {pod_name} set to {mode}"}), 200
    else:
        return jsonify({"error": "Pod not found"}), 404


@app.route('/status/<pod_name>', methods=['GET'])
def pod_status(pod_name):
    """
    Retrieve the current status of a specific pod.
    """
    if pod_name in pods_state:
        return jsonify({
            "pod_name": pod_name,
            "status": pods_state[pod_name]["status"],
            "http_mode": pods_state[pod_name]["http_mode"]
        })
    else:
        return jsonify({"error": "Pod not found"}), 404


# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)