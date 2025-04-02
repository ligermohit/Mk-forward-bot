#!/bin/bash

# Starting web application with gunicorn on port 8081
# This avoids port conflict with the Telegram bot server

echo "Starting web application on port 8081..."
gunicorn --bind 0.0.0.0:8081 --reload app:app