# Use the Python 3.12 base image
FROM registry.suse.com/bci/python:3.12

# Set the working directory
WORKDIR /app

# Copy the configuration and the script
COPY ../../configs/log_messages.json /app/log_messages.json
COPY ../../app/database.py /app/database.py

# Install necessary Python packages
RUN pip install flask

# Set the entrypoint to run the database script
CMD ["python3", "database.py"]