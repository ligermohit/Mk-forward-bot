"""
Auto-Restart Heartbeat Mechanism for the Forward Bot

This module provides a robust heartbeat mechanism that monitors the bot's 
health and automatically restarts it if any issues are detected. It works by:

1. Regularly checking if the bot is responsive
2. Monitoring critical system resources
3. Detecting potential deadlocks or hangs
4. Providing automatic recovery through restart

Usage:
  Import and start the heartbeat monitor in main.py
"""

import asyncio
import datetime
import logging
import os
import signal
import sys
import threading
import time
import psutil
from typing import Dict, Any, Optional, Callable
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [HEARTBEAT] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("heartbeat")

class HeartbeatMonitor:
    """
    Monitors the health of the bot and restarts it if necessary.
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # Check every minute
        max_memory_percent: float = 90.0,  # Restart if memory usage exceeds 90%
        max_cpu_percent: float = 95.0,  # Restart if CPU usage exceeds 95%
        telegram_client = None,
        mongodb_client = None,
        restart_callback: Optional[Callable] = None
    ):
        """
        Initialize the heartbeat monitor.
        
        Args:
            check_interval: Time between health checks in seconds
            max_memory_percent: Maximum memory usage before triggering restart
            max_cpu_percent: Maximum CPU usage before triggering restart
            telegram_client: The Telegram client instance to monitor
            mongodb_client: The MongoDB client instance to monitor
            restart_callback: Optional callback function to run before restart
        """
        self.check_interval = check_interval
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent
        self.telegram_client = telegram_client
        self.mongodb_client = mongodb_client
        self.restart_callback = restart_callback
        self.last_heartbeat = time.time()
        self.running = False
        self.process = psutil.Process(os.getpid())
        self.thread = None
        self.startup_time = time.time()
        self.check_count = 0
        
        # Statistics
        self.stats = {
            "checks": 0,
            "resource_warnings": 0,
            "restarts": 0,
            "last_restart": None,
            "telegram_errors": 0,
            "mongodb_errors": 0,
            "total_uptime": 0,
        }
    
    def start(self):
        """Start the heartbeat monitor in a separate thread."""
        if self.running:
            logger.warning("Heartbeat monitor is already running.")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Heartbeat monitor started. Checking health every %s seconds.", self.check_interval)
    
    def stop(self):
        """Stop the heartbeat monitor."""
        if not self.running:
            logger.warning("Heartbeat monitor is not running.")
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Heartbeat monitor stopped.")
    
    def update_heartbeat(self):
        """Update the heartbeat timestamp to indicate the bot is alive."""
        self.last_heartbeat = time.time()
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        while self.running:
            try:
                self._check_health()
                
                # Sleep for the check interval
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error("Error in heartbeat monitor: %s", str(e))
                # If the monitor itself fails, wait before retrying
                time.sleep(10)
    
    def _check_health(self):
        """Check various health metrics and restart if necessary."""
        self.check_count += 1
        self.stats["checks"] += 1
        
        current_time = time.time()
        uptime = current_time - self.startup_time
        self.stats["total_uptime"] = uptime
        
        memory_usage = self.process.memory_percent()
        cpu_usage = self.process.cpu_percent(interval=1.0)
        
        logger.debug(
            "Health check #%d - Memory: %.2f%%, CPU: %.2f%%, Uptime: %.2f hours",
            self.check_count, memory_usage, cpu_usage, uptime / 3600
        )
        
        # Check if we need to restart due to resource usage
        restart_reason = None
        
        if memory_usage > self.max_memory_percent:
            restart_reason = f"High memory usage: {memory_usage:.2f}% > {self.max_memory_percent:.2f}%"
            self.stats["resource_warnings"] += 1
        
        if cpu_usage > self.max_cpu_percent:
            restart_reason = f"High CPU usage: {cpu_usage:.2f}% > {self.max_cpu_percent:.2f}%"
            self.stats["resource_warnings"] += 1
        
        # Check Telegram client health if provided
        if self.telegram_client:
            try:
                # Simple check if the client is connected - don't restart based on this
                # We'll just log it for now to avoid unnecessary restarts
                is_connected = False
                
                # Try to check connection status without causing errors
                try:
                    # Use hasattr to safely check if the method exists
                    if hasattr(self.telegram_client, "is_connected"):
                        # Check if it's a method or property
                        if callable(self.telegram_client.is_connected):
                            is_connected = self.telegram_client.is_connected()
                        else:
                            is_connected = self.telegram_client.is_connected
                except Exception as e:
                    logger.warning(f"Could not check Telegram connection: {e}")
                
                if not is_connected:
                    # Just log a warning, don't restart
                    logger.warning("Telegram client appears to be disconnected")
                    self.stats["telegram_errors"] += 1
            except Exception as e:
                # Just log the error, don't restart for Telegram client issues
                logger.error("Error checking Telegram client: %s", str(e))
                self.stats["telegram_errors"] += 1
        
        # Check MongoDB client health if provided
        if self.mongodb_client:
            try:
                # Just log MongoDB issues, don't restart
                # This is to avoid issues with asyncio and Motor/PyMongo
                logger.info("Skipping MongoDB health check to avoid asyncio issues")
                self.stats["mongodb_checks"] = self.stats.get("mongodb_checks", 0) + 1
            except Exception as e:
                # Just log the error, don't restart for MongoDB issues
                logger.error("Error with MongoDB client reference: %s", str(e))
                self.stats["mongodb_errors"] += 1
        
        # Check the keep-alive web server
        try:
            # Try to connect to our keep-alive server
            response = requests.get("http://localhost:8080/ping", timeout=5)
            if response.status_code != 200 or response.text != "pong":
                restart_reason = f"Keep-alive server returned unexpected response: {response.status_code}"
        except requests.RequestException as e:
            logger.error("Keep-alive server check failed: %s", str(e))
            restart_reason = f"Keep-alive server error: {str(e)}"
        
        # If we need to restart, log it and trigger the restart
        if restart_reason:
            logger.warning("Restart triggered: %s", restart_reason)
            self._restart(reason=restart_reason)
        else:
            # Update the heartbeat timestamp since everything is OK
            self.update_heartbeat()
    
    def _check_mongodb(self, client):
        """Check if the MongoDB client is healthy."""
        try:
            # Try to ping the database
            result = client.admin.command('ping')
            return result.get('ok') == 1
        except Exception as e:
            logger.error("MongoDB ping failed: %s", str(e))
            return False
    
    def _restart(self, reason: str):
        """Restart the application."""
        self.stats["restarts"] += 1
        self.stats["last_restart"] = datetime.datetime.now().isoformat()
        
        logger.warning("Initiating restart: %s", reason)
        
        try:
            # Run the restart callback if provided
            if self.restart_callback:
                logger.info("Running restart callback...")
                try:
                    self.restart_callback(reason)
                except Exception as callback_error:
                    logger.error("Error in restart callback: %s", str(callback_error))
            
            # Log restart to a file for tracking
            restart_log_path = os.path.join(os.getcwd(), "restart_log.txt")
            with open(restart_log_path, "a") as f:
                f.write(f"{datetime.datetime.now().isoformat()} - Restart triggered: {reason}\n")
                
            # Different restart methods - we try them in order until one works
            
            # Method 1: Use os.execv to restart the process (preserves the PID)
            logger.info("Restarting using os.execv...")
            try:
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return  # If successful, we won't reach this point
            except Exception as e:
                logger.error("Failed to restart using os.execv: %s", str(e))
            
            # Method 2: Send SIGTERM to ourselves and let the process manager restart us
            logger.info("Restarting by sending SIGTERM...")
            try:
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(5)  # Wait a bit to see if SIGTERM works
            except Exception as e:
                logger.error("Failed to restart using SIGTERM: %s", str(e))
            
            # Method 3: Just exit with a non-zero code, and let the process manager restart us
            logger.info("Restarting by exiting with code 1...")
            sys.exit(1)
            
        except Exception as e:
            logger.error("Error during restart process: %s", str(e))
            # If all else fails, try the most direct method
            os._exit(1)

# Global instance that can be accessed from other modules
monitor = None

def setup_heartbeat(
    telegram_client=None,
    mongodb_client=None,
    check_interval=60,
    restart_callback=None
):
    """
    Set up and start the heartbeat monitor.
    
    Args:
        telegram_client: The Telegram client instance to monitor
        mongodb_client: The MongoDB client instance to monitor
        check_interval: Time between health checks in seconds
        restart_callback: Optional callback function to run before restart
    """
    global monitor
    
    # Create the monitor if it doesn't exist
    if monitor is None:
        monitor = HeartbeatMonitor(
            check_interval=check_interval,
            telegram_client=telegram_client,
            mongodb_client=mongodb_client,
            restart_callback=restart_callback
        )
    
    # Start the monitor
    monitor.start()
    return monitor

def get_monitor():
    """Get the global heartbeat monitor instance."""
    return monitor

def update_heartbeat():
    """Update the heartbeat timestamp to indicate the bot is alive."""
    global monitor
    if monitor:
        monitor.update_heartbeat()

def get_stats():
    """Get the current heartbeat statistics."""
    global monitor
    if monitor:
        return monitor.stats
    return {}

# Add a Flask endpoint for the heartbeat status
def register_flask_endpoints(app):
    """Register Flask endpoints for the heartbeat status."""
    @app.route('/heartbeat_monitor')
    def heartbeat_monitor_status():
        """Endpoint for checking heartbeat status."""
        stats = get_stats()
        return {
            "status": "healthy" if monitor and monitor.running else "not_running",
            "stats": stats,
            "uptime": time.time() - monitor.startup_time if monitor else 0,
            "timestamp": datetime.datetime.now().isoformat()
        }

# For testing the module directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create and start the monitor
    def mock_restart_callback(reason):
        print(f"Mock restart triggered: {reason}")
    
    monitor = HeartbeatMonitor(
        check_interval=10,  # Check every 10 seconds for testing
        restart_callback=mock_restart_callback
    )
    monitor.start()
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping heartbeat monitor...")
        monitor.stop()