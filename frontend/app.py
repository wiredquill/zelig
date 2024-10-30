from flask import Flask, jsonify, render_template, redirect, url_for
import requests
import threading
import time
import yaml

app = Flask(__name__)

# Load module configuration from YAML file
def load_module_config():
    with open("modules-config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["modules"]

# Initialize modules from config file
modules = load_module_config()

# Function to toggle mode of a module
def toggle_module_mode(module_name):
    module = modules.get(module_name)
    if module:
        toggle_url = f"{module['url']}/on" if module["status"] == "Normal" else f"{module['url']}/off"
        try:
            requests.get(toggle_url, timeout=5)
            return True
        except requests.RequestException:
            return False

# Background job to update status every 60 seconds
def update_status():
    while True:
        for name, module in modules.items():
            try:
                response = requests.get(module["url"], timeout=5)
                if response.status_code == 200:
                    module["status"] = "Normal"
                elif response.status_code == 500:
                    module["status"] = "Error"
            except requests.RequestException:
                module["status"] = "Unknown"
        time.sleep(60)

# Endpoint to toggle mode
@app.route("/toggle/<module_name>")
def toggle(module_name):
    if toggle_module_mode(module_name):
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