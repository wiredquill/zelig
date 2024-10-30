from flask import Flask, jsonify
import logging
import time
import schedule
import threading
import yaml
from pyfiglet import Figlet
import sys

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

server_name = config.get("server_name", "Default Server")
log_message = config.get("log_message", "Default log message.")
log_interval = config.get("log_interval", 60)  # Default to 60 seconds if not specified
error_mode = False

# Configure logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')
app = Flask(__name__)

# ASCII Art for server name
def display_server_name():
    figlet = Figlet(font="slant")
    print(figlet.renderText(server_name))

# Periodic logging function
def log_message_periodically():
    logging.info(log_message)

# Schedule periodic logging based on config interval
schedule.every(log_interval).seconds.do(log_message_periodically)

# Run scheduled tasks
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# HTTP Routes
@app.route('/')
def root():
    global error_mode
    if error_mode:
        return "Internal Server Error", 500
    return jsonify(message="ok"), 200

@app.route('/500')
def set_error_mode():
    global error_mode
    error_mode = True
    return jsonify(message="500 mode activated"), 200

@app.route('/stop500')
def stop_error_mode():
    global error_mode
    error_mode = False
    return jsonify(message="500 mode deactivated"), 200

if __name__ == "__main__":
    # Display ASCII server name on startup
    display_server_name()

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start the Flask server
    app.run(host="0.0.0.0", port=8080)