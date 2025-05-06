# Use official Python image from Docker Hub
FROM python:3.9-slim

# Set environment variables for headless operation
ENV DISPLAY=:99

# Install necessary dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium-driver \
    chromium \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libdbus-glib-1-2 \
    libnspr4 \
    libxt6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . /app

# Set the working directory for the Flask app
WORKDIR /app

# Expose the port Flask will run on
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
