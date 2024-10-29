# Use the Python 3.12 base image
FROM registry.suse.com/bci/python:3.12

# Set the working directory
WORKDIR /app

# Copy the configuration, script, and HTML template files
COPY ../../configs/log_messages.json /app/log_messages.json
COPY ../../app/frontend.py /app/frontend.py
COPY ../../app/templates /app/templates

# Install necessary Python packages
RUN pip install flask

# Expose the port for the frontend
EXPOSE 5000

# Set the entrypoint to run the frontend script
CMD ["python3", "frontend.py"]