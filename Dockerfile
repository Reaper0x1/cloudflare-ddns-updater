FROM python:3.11-alpine

# Set timezone
ENV TZ="Europe/Berlin"

# Install tzdata
RUN apk add --no-cache tzdata bind-tools

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install apscheduler requests

# Set working directory
WORKDIR /app

# Copy your script and encryption files to the container
COPY ./ddns-updater.py /app/script.py

# Make your script executable
RUN chmod +x /app/script.py

# Start cron and log output to console
CMD ["python", "/app/script.py"]