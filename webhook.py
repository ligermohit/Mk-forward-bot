import http.server
import socketserver
import json
import threading
import time
import datetime
import os
import psutil

PORT = 8080
PING_COUNTER = 0
LAST_PING_TIME = None
START_TIME = time.time()

# Try to import Config
try:
    from config import Config
    CONFIG_LOADED = True
except Exception as e:
    print(f"Error importing Config in webhook.py: {e}")
    CONFIG_LOADED = False
    # Create a minimal Config class as a fallback
    class Config:
        API_ID = 0
        API_HASH = ""
        BOT_TOKEN = ""
        BOT_SESSION = "vjbot_new"

# HTML template for web interface
HTML_TEMPLATE = """
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
                <span class="status-label">Total Pings:</span>
                <span>{ping_count}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Last Ping:</span>
                <span>{last_ping}</span>
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

class PingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global PING_COUNTER, LAST_PING_TIME
        
        if self.path == "/ping":
            # Update stats
            PING_COUNTER += 1
            LAST_PING_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "online",
                "message": "Bot is running",
                "ping_count": PING_COUNTER,
                "timestamp": LAST_PING_TIME
            }
            
            self.wfile.write(json.dumps(response).encode())
            print(f"[PING] Received ping request at {LAST_PING_TIME}")
            return
        elif self.path == "/":
            # Update stats
            PING_COUNTER += 1
            LAST_PING_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
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
            uptime = datetime.timedelta(seconds=int(time.time() - START_TIME))
            
            # Bot info
            bot_username = Config.BOT_SESSION if CONFIG_LOADED else "Forward_Clone2bot"
            api_status = "Configured" if CONFIG_LOADED and Config.API_ID and Config.API_HASH else "Missing"
                
            # Generate HTML content
            html_content = HTML_TEMPLATE.format(
                bot_username=bot_username,
                api_status=api_status,
                uptime=uptime,
                memory_info=memory_info,
                disk_info=disk_info,
                ping_count=PING_COUNTER,
                last_ping=LAST_PING_TIME or "Never"
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
            return
        
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Disable default logging to keep output clean
        return

def run_server():
    with socketserver.TCPServer(("0.0.0.0", PORT), PingHandler) as httpd:
        print(f"Starting server on port {PORT}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")

def start_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    print(f"Server started on port {PORT} in background")
    
    return server_thread

if __name__ == "__main__":
    print("Starting simple webhook server for uptime monitoring...")
    server_thread = start_server()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)
            print(f"Server is still running. Total pings: {PING_COUNTER}")
    except KeyboardInterrupt:
        print("Shutting down...")