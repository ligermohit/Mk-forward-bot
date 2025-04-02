"""
Script to keep the Replit project alive by serving a simple HTTP endpoint.
This is used with external pinging services like UptimeRobot to keep the bot running 24/7.

UptimeRobot Setup Instructions:
1. Go to https://uptimerobot.com/ and create a free account
2. After logging in, click "Add New Monitor"
3. Select "HTTP(s)" as the monitor type
4. Enter a name like "Telegram Forward Bot"
5. For the URL, enter your Replit app URL: https://your-repl-name.your-username.repl.co/ping
   (We are using the default port for simplicity)
6. Set monitoring interval to 5 minutes
7. Save the monitor

This will ping your bot every 5 minutes, keeping it alive even when you're not using Replit.
"""

from flask import Flask, jsonify, render_template_string
from threading import Thread
import logging
import datetime
import psutil
import os
import time

# Create global variable to store startup time
start_time = time.time()

# Try to import heartbeat module
try:
    from heartbeat import get_stats, get_monitor, register_flask_endpoints
    heartbeat_available = True
except ImportError:
    heartbeat_available = False

app = Flask(__name__)

# Disable flask log messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# HTML template for status page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Forward Bot - Status</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        h2 {
            color: #2196F3;
            margin-top: 10px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .status-card {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            background-color: #e8f5e9;
            border-left: 5px solid #4CAF50;
        }
        .heartbeat-card {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            background-color: #e3f2fd;
            border-left: 5px solid #2196F3;
        }
        .mongo-card {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            background-color: #fff3e0;
            border-left: 5px solid #FF9800;
        }
        .status-item {
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .progress-bar {
            height: 8px;
            width: 100%;
            background-color: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill {
            height: 100%;
            background-color: #4CAF50;
            border-radius: 4px;
        }
        .progress-high {
            background-color: #f44336;
        }
        .progress-med {
            background-color: #FF9800;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            font-size: 12px;
            border-radius: 12px;
            background-color: #e0e0e0;
            margin-left: 5px;
        }
        .badge-success {
            background-color: #4CAF50;
            color: white;
        }
        .badge-warning {
            background-color: #FF9800;
            color: white;
        }
        .badge-danger {
            background-color: #f44336;
            color: white;
        }
        .badge-info {
            background-color: #2196F3;
            color: white;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #777;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Forward Bot Status</h1>

        <div class="status-card">
            <h2>System Status</h2>
            <div class="status-item">
                <strong>Status:</strong> 🟢 Online
            </div>
            <div class="status-item">
                <strong>Uptime:</strong> {{ uptime }}
            </div>
            <div class="status-item">
                <strong>CPU Usage:</strong> {{ cpu_usage }}%
                <div class="progress-bar">
                    <div class="progress-fill {% if cpu_usage > 80 %}progress-high{% elif cpu_usage > 50 %}progress-med{% endif %}" style="width: {{ cpu_usage }}%"></div>
                </div>
            </div>
            <div class="status-item">
                <strong>Memory Usage:</strong> {{ memory_usage }}%
                <div class="progress-bar">
                    <div class="progress-fill {% if memory_usage > 80 %}progress-high{% elif memory_usage > 50 %}progress-med{% endif %}" style="width: {{ memory_usage }}%"></div>
                </div>
            </div>
            <div class="status-item">
                <strong>Last Checked:</strong> {{ current_time }}
            </div>
        </div>

        {% if heartbeat_available %}
        <div class="heartbeat-card">
            <h2>Heartbeat Monitor</h2>
            <div class="status-item">
                <strong>Status:</strong> 
                {% if hb_status == 'Active' %}
                    🟢 Active <span class="badge badge-success">Running</span>
                {% else %}
                    🔴 Inactive <span class="badge badge-danger">Stopped</span>
                {% endif %}
            </div>
            <div class="status-item">
                <strong>Monitor Uptime:</strong> {{ hb_uptime }}
            </div>
            <div class="status-item">
                <strong>Health Checks:</strong> {{ hb_checks }}
                {% if hb_checks > 0 %}<span class="badge badge-info">{{ hb_checks }}</span>{% endif %}
            </div>
            <div class="status-item">
                <strong>Auto-Restarts:</strong> {{ hb_restarts }}
                {% if hb_restarts > 0 %}<span class="badge badge-warning">{{ hb_restarts }}</span>{% endif %}
            </div>
            <div class="status-item">
                <strong>Last Restart:</strong> {{ hb_last_restart }}
            </div>
        </div>
        {% endif %}

        <div class="mongo-card">
            <h2>Database Status</h2>
            <div class="status-item">
                <strong>MongoDB:</strong> 
                {% if db_status == 'Connected' %}
                    🟢 Connected <span class="badge badge-success">Online</span>
                {% else %}
                    🔴 Disconnected <span class="badge badge-danger">Offline</span>
                {% endif %}
            </div>
            <div class="status-item">
                <strong>Database:</strong> {{ db_uri }}
            </div>
        </div>

        <div class="footer">
            <p>This page is used by UptimeRobot to keep the bot running 24/7.</p>
            <p>The Heartbeat Monitor ensures the bot stays running even if issues are detected.</p>
            <p>© 2025 Forward Bot</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Homepage showing detailed bot status with HTML template"""
    # Calculate uptime
    uptime_seconds = time.time() - start_time
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes"

    # Get system stats
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory_usage = psutil.virtual_memory().percent
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if MongoDB connection is available
    try:
        from database import db
        db_status = "Connected" if hasattr(db, 'connection_ok') and db.connection_ok else "Disconnected"
        db_uri_masked = "MongoDB Atlas" if "mongodb+srv" in os.environ.get("MONGODB_URI", "") else "Unknown"
    except Exception as e:
        db_status = "Error"
        db_uri_masked = f"Not configured ({str(e)[:30]}...)"

    # Get heartbeat status if available
    hb_status = "Not Available"
    hb_uptime = "N/A"
    hb_checks = 0
    hb_restarts = 0
    hb_last_restart = "Never"

    if heartbeat_available:
        try:
            hb_monitor = get_monitor()
            if hb_monitor:
                hb_stats = get_stats()
                hb_status = "Active" if hb_monitor.running else "Inactive"

                # Format heartbeat uptime
                hb_uptime_seconds = time.time() - hb_monitor.startup_time if hb_monitor.running else 0
                days, remainder = divmod(hb_uptime_seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
                hb_uptime = f"{int(days)}d {int(hours)}h {int(minutes)}m"

                hb_checks = hb_stats.get("checks", 0)
                hb_restarts = hb_stats.get("restarts", 0)
                hb_last_restart = hb_stats.get("last_restart", "Never")
        except Exception as e:
            hb_status = f"Error: {str(e)[:30]}"

    # Render HTML template with stats
    return render_template_string(
        HTML_TEMPLATE,
        uptime=uptime_str,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        current_time=current_time,
        heartbeat_available=heartbeat_available,
        hb_status=hb_status,
        hb_uptime=hb_uptime,
        hb_checks=hb_checks,
        hb_restarts=hb_restarts,
        hb_last_restart=hb_last_restart,
        db_status=db_status,
        db_uri=db_uri_masked
    )

@app.route('/ping')
def ping():
    """Simple ping endpoint for uptime monitors"""
    return "pong"

@app.route('/status')
def status():
    """JSON endpoint for status checks"""
    status_data = {
        'status': 'online',
        'uptime': time.time() - start_time,
        'cpu_usage': psutil.cpu_percent(interval=0.5),
        'memory_usage': psutil.virtual_memory().percent,
        'timestamp': datetime.datetime.now().isoformat()
    }

    # Add database status if available
    try:
        from database import db
        status_data['database'] = {
            'status': 'connected' if hasattr(db, 'connection_ok') and db.connection_ok else 'disconnected',
            'type': 'mongodb'
        }
    except:
        status_data['database'] = {'status': 'unavailable'}

    # Add heartbeat status if available
    if heartbeat_available:
        try:
            hb_monitor = get_monitor()
            if hb_monitor:
                hb_stats = get_stats()
                status_data['heartbeat'] = {
                    'status': 'active' if hb_monitor.running else 'inactive',
                    'uptime': time.time() - hb_monitor.startup_time if hb_monitor.running else 0,
                    'checks': hb_stats.get('checks', 0),
                    'restarts': hb_stats.get('restarts', 0),
                    'last_restart': hb_stats.get('last_restart', None),
                }
        except:
            status_data['heartbeat'] = {'status': 'error'}

    return jsonify(status_data)

@app.route('/heartbeat')
def heartbeat_status():
    """JSON endpoint for heartbeat monitoring status"""
    if not heartbeat_available:
        return jsonify({
            'status': 'unavailable',
            'error': 'Heartbeat monitoring is not enabled'
        }), 404

    try:
        hb_monitor = get_monitor()
        if not hb_monitor:
            return jsonify({
                'status': 'not_initialized',
                'error': 'Heartbeat monitor not initialized'
            }), 404

        hb_stats = get_stats()
        return jsonify({
            'status': 'active' if hb_monitor.running else 'inactive',
            'uptime': time.time() - hb_monitor.startup_time if hb_monitor.running else 0,
            'checks': hb_stats.get('checks', 0),
            'restarts': hb_stats.get('restarts', 0),
            'last_restart': hb_stats.get('last_restart', None),
            'resource_warnings': hb_stats.get('resource_warnings', 0),
            'telegram_errors': hb_stats.get('telegram_errors', 0),
            'mongodb_errors': hb_stats.get('mongodb_errors', 0),
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def run():
    """Run the Flask app on port 8080"""
    # Use port 8080 to match workflow settings
    app.run(host='0.0.0.0', port=8080, debug=False)

def start_server():
    """Start the keep-alive server in a background thread"""
    # Register heartbeat endpoints if available
    if heartbeat_available:
        try:
            register_flask_endpoints(app)
            print("Registered heartbeat monitoring endpoints")
        except Exception as e:
            print(f"Failed to register heartbeat endpoints: {e}")

    # Start the server
    t = Thread(target=run)
    t.daemon = True  # The thread will exit when the main program exits
    t.start()
    print("Keep-alive server started on port 8080")

    # Start self-pinging in a separate thread
    self_ping_thread = Thread(target=self_ping_service)
    self_ping_thread.daemon = True
    self_ping_thread.start()
    print("Self-ping service started to keep bot alive")

def self_ping_service():
    """A simple service that pings our own endpoints to keep the bot alive"""
    import time
    import requests
    from datetime import datetime

    while True:
        try:
            # Ping the single Flask app endpoint
            response = requests.get("http://localhost:8080/ping", timeout=10)
            if response.status_code == 200:
                print(f"[SELF-PING] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Ping successful")

        except Exception as e:
            print(f"[SELF-PING] Error during self-ping: {str(e)}")

        # Sleep for 5 minutes
        time.sleep(300)

if __name__ == '__main__':
    # This can be run directly for testing
    app.run(host='0.0.0.0', port=8080, debug=False)