# Use the SUSE BCI Python 3.12 image
FROM registry.suse.com/bci/python:3.12

# Install required packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application files
COPY app.py .
COPY config.yaml .

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["python3", "app.py"]