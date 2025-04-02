#!/bin/bash

# Starting web application with waitress on port 8081
# This avoids port conflict with the Telegram bot server

echo "Starting web application on port 8081..."
python run_webapp.py