"""
Web interface for the Telegram Forward Bot
This provides a simple web UI that runs on port 8081 to avoid conflicts with the main bot.
"""

from flask import Flask, render_template_string, jsonify, Response
import os
import datetime
import psutil
import time
import threading
import requests

# Handle Config import with error handling
try:
    from config import Config
except Exception as e:
    print(f"Error importing Config in web_interface.py: {e}")
    # Create a minimal Config class as a fallback
    class Config:
        API_ID = 0
        API_HASH = ""
        BOT_TOKEN = ""
        BOT_SESSION = "vjbot_new"

# Create global variable to store startup time
start_time = time.time()

app = Flask(__name__)

# Basic HTML template with dark theme
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VJ Forward Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #222;
            color: #eee;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #333;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        h1, h2 {
            color: #4CAF50;
            text-align: center;
        }
        .status-card {
            background-color: #444;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            border-bottom: 1px solid #555;
            padding-bottom: 10px;
        }
        .status-label {
            font-weight: bold;
            color: #90CAF9;
        }
        .btn {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
            margin: 0 auto;
        }
        .center {
            text-align: center;
            margin-top: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>VJ Forward Bot</h1>
        <p style="text-align: center;">A powerful Telegram message forwarding bot</p>
        
        <div class="status-card">
            <h2>Bot Status</h2>
            <div class="status-item">
                <span class="status-label">Bot Username:</span>
                <span>@{{ bot_username }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">API Configuration:</span>
                <span>{{ api_status }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Uptime:</span>
                <span>{{ uptime }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Memory Usage:</span>
                <span>{{ memory_usage }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Disk Usage:</span>
                <span>{{ disk_usage }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Web Interface:</span>
                <span>Online</span>
            </div>
        </div>
        
        <div class="status-card">
            <h2>Features</h2>
            <ul>
                <li>Forward messages from one channel to another</li>
                <li>Support for private and public channels</li>
                <li>Custom caption support</li>
                <li>Filter messages by type and content</li>
                <li>Skip duplicate messages</li>
                <li>Advanced message handling</li>
            </ul>
        </div>
        
        <div class="center">
            <a href="https://t.me/{{ bot_username }}" class="btn">
                Open Bot in Telegram
            </a>
        </div>
        
        <div class="footer">
            <p>Developed by MR. MOHIT | <a href="https://t.me/itz_THANOS" style="color: #4CAF50;">Contact ME</a></p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    """Home page showing bot status information"""
    # Extract bot username from token or use placeholder
    bot_token = Config.BOT_TOKEN
    bot_username = "Forward_Clone2bot"
    
    if bot_token and ":" in bot_token:
        try:
            # Extract username from token format (bot_id:token_string)
            bot_id = bot_token.split(":")[0]
            # Use actual bot username, or fallback to known username
            bot_username = "Forward_Clone2bot" 
        except Exception as e:
            print(f"Error parsing bot token: {e}")
    
    # Get system info
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        memory_usage = f"{memory.percent}%"
        disk_usage = f"{disk.percent}%"
    except Exception as e:
        print(f"Error getting system info: {e}")
        memory_usage = "N/A"
        disk_usage = "N/A"
    
    # Calculate uptime
    uptime = datetime.timedelta(seconds=int(time.time() - start_time))
    
    api_status = "Configured" if Config.API_ID and Config.API_HASH else "Missing"
    
    return render_template_string(
        HTML_TEMPLATE, 
        bot_username=bot_username,
        api_status=api_status,
        uptime=uptime,
        memory_usage=memory_usage,
        disk_usage=disk_usage
    )

@app.route('/ping')
def ping():
    """Endpoint that can be used by UptimeRobot or similar services to keep the bot alive"""
    # Get system info
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify({
        'status': 'alive',
        'message': 'Web interface is running!',
        'uptime': uptime,
        'memory_used_percent': memory.percent,
        'disk_used_percent': disk.percent,
        'bot_username': Config.BOT_SESSION
    })

@app.route('/healthcheck')
def healthcheck():
    """Simple health check endpoint"""
    return 'OK', 200

def run_web_app():
    """Run the Flask web app"""
    app.run(host="0.0.0.0", port=8081, debug=False)  # Disable debug mode in thread

def start_web_interface():
    """Start the web interface in a separate thread"""
    try:
        webapp_thread = threading.Thread(target=run_web_app)
        webapp_thread.daemon = True
        webapp_thread.start()
        print("Web interface started on port 8081")
    except Exception as e:
        print(f"Error starting web interface: {e}")
    
if __name__ == "__main__":
    run_web_app()