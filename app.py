from flask import Flask, render_template_string, jsonify
import os
import datetime
import psutil
import time
from threading import Thread

# Handle Config import with error handling
try:
    from config import Config
except Exception as e:
    print(f"Error importing Config in app.py: {e}")
    # Create a minimal Config class as a fallback
    class Config:
        API_ID = 0
        API_HASH = ""
        BOT_TOKEN = ""
        BOT_SESSION = "vjbot_new"

# Create global variable to store startup time
start_time = time.time()

# Try to import heartbeat module
try:
    from heartbeat import get_stats, get_monitor, register_flask_endpoints
    heartbeat_available = True
except ImportError:
    heartbeat_available = False

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VJ Forward Bot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding: 20px;
            background-color: #343a40;
            color: #f8f9fa;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            margin-bottom: 20px;
            border-radius: 8px;
        }
        .btn-secondary {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card bg-dark text-white p-4">
            <h1 class="display-4 text-center">VJ Forward Bot</h1>
            <p class="lead text-center">A Telegram message forwarding bot</p>
            <hr>
            
            <div class="card bg-secondary p-3 mt-4">
                <h3>Bot Status</h3>
                <p><strong>Bot Username:</strong> {{ bot_username }}</p>
                <p><strong>API Config:</strong> {{ api_status }}</p>
                <p><strong>Database:</strong> Connected</p>
                <p><strong>Web Interface:</strong> Running</p>
            </div>
            
            <div class="card bg-secondary p-3 mt-3">
                <h3>Features</h3>
                <ul>
                    <li>Forward messages from one channel to another</li>
                    <li>Support for private and public channels</li>
                    <li>Custom caption support</li>
                    <li>Filter messages by type and content</li>
                    <li>Skip duplicate messages</li>
                </ul>
            </div>
            
            <div class="text-center mt-4">
                <a href="https://t.me/{{ bot_username }}" class="btn btn-primary btn-lg" target="_blank">
                    Open Bot in Telegram
                </a>
            </div>
            
            <div class="text-center mt-4 text-muted">
                <p>Developed by MR. MOHIT | <a href="https://t.me/itz_THANOS" class="text-info">Contact ME</a></p>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def hello_world():
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
        memory_info = f"{memory.percent}%"
        disk_info = f"{disk.percent}%"
    except Exception as e:
        print(f"Error getting system info: {e}")
        memory_info = "N/A"
        disk_info = "N/A"
    
    # Calculate uptime
    uptime = datetime.timedelta(seconds=int(time.time() - start_time))
    
    api_status = "Configured" if Config.API_ID and Config.API_HASH else "Missing"
    
    # Create HTML template with status information
    FULL_HTML = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VJ Forward Bot</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #222;
                color: #eee;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: #333;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }}
            h1, h2 {{
                color: #4CAF50;
                text-align: center;
            }}
            .status-card {{
                background-color: #444;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
            }}
            .status-item {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                border-bottom: 1px solid #555;
                padding-bottom: 10px;
            }}
            .status-label {{
                font-weight: bold;
                color: #90CAF9;
            }}
            .btn {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                text-align: center;
                margin: 0 auto;
            }}
            .center {{
                text-align: center;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #999;
                font-size: 14px;
            }}
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
                    <span>@{bot_username}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">API Config:</span>
                    <span>{api_status}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Uptime:</span>
                    <span>{uptime}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Memory Usage:</span>
                    <span>{memory_info}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Disk Usage:</span>
                    <span>{disk_info}</span>
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
                <a href="https://t.me/{bot_username}" class="btn">
                    Open Bot in Telegram
                </a>
            </div>
            
            <div class="footer">
                <p>Developed by MR. MOHIT | <a href="https://t.me/itz_THANOS" style="color: #4CAF50;">Contact ME</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return FULL_HTML

@app.route('/ping')
def ping():
    """Endpoint that can be used by UptimeRobot or similar services to keep the bot alive"""
    # Get system info
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify({
        'status': 'alive',
        'message': 'Bot is running!',
        'uptime': uptime,
        'memory_used_percent': memory.percent,
        'disk_used_percent': disk.percent,
        'bot_username': Config.BOT_SESSION
    })

@app.route('/healthcheck')
def healthcheck():
    """Simple health check endpoint"""
    return 'OK', 200


# We're using an alternative port for the web interface
# since the telegram bot workflow already uses port 8080
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
