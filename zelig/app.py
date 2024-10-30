from flask import Flask, jsonify
import logging
import time
import schedule
import threading
import yaml
import os
from pyfiglet import Figlet
import sys

# Initial configuration load
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()

# Load configurable values
server_name = config.get("server_name", "Default Server")
log_message = config.get("log_message", "Default log message.")
error_log_message = config.get("error_log_message", "Default error log message.")  # Log message for error mode
log_interval = config.get("log_interval", 60)  # Default to 60 seconds
http_ok_message = config.get("http_ok_message", "ok")  # Default HTTP OK message
http_500_message = config.get("http_500_message", "Internal Server Error")  # Default 500 error message
http_request_log_message = config.get("http_request_log_message", "HTTP request received at root path")
http_on_log_message = config.get("http_500_activate_log_message", "Error mode activated")
http_off_log_message = config.get("http_500_deactivate_log_message", "Error mode deactivated")
initial_error_mode = config.get("initial_error_mode", False)  # Default to False if not specified
error_mode = initial_error_mode  # Set initial error mode based on config

# Track config file modification time
config_path = "config.yaml"
last_modified_time = os.path.getmtime(config_path)

# Configure logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')
app = Flask(__name__)

# ASCII Art for server name
def display_server_name():
    figlet = Figlet(font="slant")
    print(figlet.renderText(server_name))

# Periodic logging function with conditional error mode check
def log_message_periodically():
    if error_mode:
        logging.info(error_log_message)
    else:
        logging.info(log_message)

# Schedule periodic logging based on config interval
schedule.every(log_interval).seconds.do(log_message_periodically)

# Run scheduled tasks
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Check for config updates and apply changes to error_mode dynamically
def check_config_updates():
    global error_mode, last_modified_time

    # Check if the config file has been modified
    current_modified_time = os.path.getmtime(config_path)
    if current_modified_time != last_modified_time:
        last_modified_time = current_modified_time
        new_config = load_config()

        # Update error mode based on new config
        new_error_mode = new_config.get("initial_error_mode", False)
        if new_error_mode != error_mode:
            error_mode = new_error_mode
            logging.info(f"Error mode updated to {'enabled' if error_mode else 'disabled'} due to config change")

# Start a separate thread for checking config updates
def start_config_watcher():
    while True:
        check_config_updates()
        time.sleep(5)  # Check every 5 seconds

# HTTP Routes
@app.route('/')
def root():
    global error_mode
    # Log the appropriate message based on the current mode
    if error_mode:
        logging.info(error_log_message)
        return jsonify(message=http_500_message), 500
    else:
        logging.info(log_message)
        return jsonify(message=http_ok_message), 200

@app.route('/on')
def enable_error_mode():
    global error_mode
    error_mode = True
    # Log error mode activation
    logging.info(http_on_log_message)
    return jsonify(message="Error mode activated"), 200

@app.route('/off')
def disable_error_mode():
    global error_mode
    error_mode = False
    # Log error mode deactivation
    logging.info(http_off_log_message)
    return jsonify(message="Error mode deactivated"), 200

if __name__ == "__main__":
    # Display ASCII server name on startup
    display_server_name()

    # Log the initial state of error mode after the ASCII art
    initial_state = "Error mode is enabled" if error_mode else "Error mode is disabled"
    logging.info(f"Initial state: {initial_state}")

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start the config watcher in a separate thread
    config_watcher_thread = threading.Thread(target=start_config_watcher, daemon=True)
    config_watcher_thread.start()

    # Start the Flask server
    app.run(host="0.0.0.0", port=8080)