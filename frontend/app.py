from flask import Flask, jsonify, render_template, redirect, url_for, request
import requests
import threading
import time
import yaml

app = Flask(__name__)

# Load module configuration from YAML file
def load_module_config():
    with open("modules-config.yaml", "r") as file:
        config = yaml.safe_load(file)
    # Initialize each module's last_message to "No message received"
    for module in config["modules"].values():
        module["last_message"] = "No message received"
    return config["modules"]

# Initialize modules from config file
modules = load_module_config()

# Function to toggle mode of a module
def toggle_module_mode(module_name, action):
    module = modules.get(module_name)
    if module:
        toggle_url = f"{module['url']}/on" if action == "on" else f"{module['url']}/off"
        try:
            response = requests.get(toggle_url, timeout=5)
            if response.status_code == 200:
                module["last_message"] = response.json().get("message", "No message")
            else:
                module["last_message"] = "Error"
            return True
        except requests.RequestException:
            module["last_message"] = "Failed to connect"
            return False

# Background job to update status every 60 seconds
def update_status():
    while True:
        for name, module in modules.items():
            try:
                response = requests.get(module["url"], timeout=5)
                if response.status_code == 200:
                    module["status"] = "Normal"
                    module["last_message"] = response.json().get("message", "No message")
                else:
                    module["status"] = "Error"
                    module["last_message"] = response.json().get("message", "Error")
            except requests.RequestException:
                module["status"] = "Unknown"
                module["last_message"] = "No connection"
        time.sleep(60)

# Endpoint to send a request to the service (simulating "Send Request")
@app.route("/send_request/<module_name>", methods=["POST"])
def send_request(module_name):
    module = modules.get(module_name)
    if module:
        try:
            response = requests.get(module["url"], timeout=5)
            if response.status_code == 200:
                module["last_message"] = response.json().get("message", "No message")
            else:
                module["last_message"] = "Error"
        except requests.RequestException:
            module["last_message"] = "Failed to connect"
    return redirect(url_for("index"))

# Endpoint to toggle failure mode
@app.route("/toggle/<module_name>", methods=["POST"])
def toggle(module_name):
    action = request.form.get("action")
    if toggle_module_mode(module_name, action):
        return redirect(url_for("index"))
    return "Failed to toggle mode", 500

# Main dashboard page
@app.route("/")
def index():
    return render_template("index.html", modules=modules)

# Start the background status updater
status_thread = threading.Thread(target=update_status, daemon=True)
status_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)