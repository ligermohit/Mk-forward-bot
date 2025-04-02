"""
Run webapp script that avoids port conflict with the Telegram bot.
This script sets up a web server on port 8081 for the web interface.
"""

from app import app
from waitress import serve
import os

if __name__ == "__main__":
    print("Starting web application on port 8081...")
    # Use waitress for a more production-ready server
    serve(app, host="0.0.0.0", port=8081)