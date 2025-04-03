# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio, logging, os, sys
from config import Config
from pyrogram import Client as VJ, idle
from pyrogram import types  # Add explicit import for types
from typing import Union, Optional, AsyncGenerator
from logging.handlers import RotatingFileHandler
from plugins.regix import restart_forwards
from heartbeat import setup_heartbeat

# Import keep-alive webhook for Uptime Robot
from keep_alive_webhook import start_webhook

# Import web interface
from web_interface import start_web_interface

# Start the keep alive webhook and web interface
start_webhook()
start_web_interface()
print("Started keep-alive webhook on port 8080")
print("Started web interface on port 8081")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

if __name__ == "__main__":
    # Note: The keep-alive server is now integrated with the main Flask app
    # and starts automatically with the "Start application" workflow
    print("Bot starting - web server runs in separate workflow")
    
    VJBot = VJ(
        Config.BOT_SESSION,
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        sleep_threshold=5,  # Increased from 5 to 10 to avoid FloodWait
        plugins=dict(root="plugins"),
        workers=5,  # Reduced worker threads from 20 to 5 to avoid FloodWait
        in_memory=True  # Use in-memory session for faster access
    )  
    # We'll use the built-in functionality of pyrofork/pyrogram for iter_messages
               
    async def main():
        # Check if all required credentials are available
        if not Config.API_ID or not Config.API_HASH or not Config.BOT_TOKEN:
            print("ERROR: Missing Telegram API credentials")
            print("Please make sure API_ID, API_HASH, and BOT_TOKEN are properly set")
            print("Exiting...")
            return
            
        while True:
            try:
                print("Attempting to start the bot...")
                try:
                    # Here we'll add special handling for FloodWait errors
                    from pyrogram.errors import FloodWait
                    
                    try:
                        await VJBot.start()
                    except FloodWait as fw:
                        # Extract the wait time directly from the FloodWait exception
                        wait_time = fw.value  # This is the seconds to wait
                        print(f"FloodWait detected! Telegram requires a wait of {wait_time} seconds")
                        print(f"Waiting for {wait_time} seconds...")
                        await asyncio.sleep(wait_time + 10)  # Add a buffer of 10 seconds
                        # Try again after waiting
                        await VJBot.start()
                        
                    bot_info = await VJBot.get_me()
                    print(f"Bot Started. @{bot_info.username} ({bot_info.first_name})")
                except Exception as e:
                    print(f"Error during bot startup: {e}")
                    raise
                    
                # Temporarily disable restart_forwards due to issues with asyncio loops
                # await restart_forwards(VJBot)
                print("Bot is now ready to use!")
                
                # Setup keep-alive mechanism for Replit with logging
                import datetime
                import pytz
                
                # Log start time
                ist_tz = pytz.timezone('Asia/Kolkata')
                start_time = datetime.datetime.now(ist_tz).strftime("%d-%m-%Y %H:%M:%S")
                print(f"Bot started at: {start_time} (IST)")
                
                # Try to send initial log message
                try:
                    from plugins.logger import log_structured_message
                    
                    # Send a log message to the log channel
                    await log_structured_message(
                        VJBot,
                        "bot_start",
                        details={"uptime_check": True},
                        user_info={"id": 0, "name": "System"}
                    )
                except Exception as e:
                    print(f"Could not send initial log: {e}")
                
                # Temporarily disable heartbeat monitor due to Telegram API FloodWait issues
                print("Heartbeat monitor disabled to avoid Telegram API issues")
                
                # Keep-alive loop
                try:
                    while True:
                        await asyncio.sleep(600)  # Sleep for 10 minutes
                        
                        # Get current time in IST
                        current_time = datetime.datetime.now(ist_tz).strftime("%d-%m-%Y %H:%M:%S")
                        print(f"Bot is still running... Last check: {current_time} (IST)")
                        
                        # Try to log the keep-alive status
                        try:
                            # Send a keep-alive message to the log channel every 6 hours (36 checks)
                            if hasattr(VJBot, 'keep_alive_count'):
                                VJBot.keep_alive_count += 1
                            else:
                                VJBot.keep_alive_count = 1
                                
                            # Log only every 36th check (6 hours)
                            if VJBot.keep_alive_count % 36 == 0:
                                from plugins.logger import log_structured_message
                                from database import db
                                
                                # Get statistics
                                total_users = await db.total_users_count()
                                total_forwards = await db.forwad_count()
                                
                                # Send a log message to the log channel
                                await log_structured_message(
                                    VJBot,
                                    "keep_alive",
                                    details={
                                        "uptime_check": True,
                                        "total_users": total_users,
                                        "active_forwards": total_forwards,
                                        "check_count": VJBot.keep_alive_count
                                    },
                                    user_info={"id": 0, "name": "System"}
                                )
                        except Exception as e:
                            print(f"Keep-alive log error: {e}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                
                break
            except Exception as e:
                # Just print the error and wait a fixed time
                # These are typically flood wait errors
                print(f"ERROR during startup: {e}")
                print("Waiting for 5 minutes before retrying...")
                await asyncio.sleep(300)  # 5 minute wait
                continue

    # Use the default event loop instead of creating a new one
    loop = asyncio.get_event_loop()
    
    # Function to restart the bot if it crashes
    def run_bot_with_restart():
        import time
        import traceback
        
        while True:
            try:
                # Run the bot
                print("Starting bot...")
                loop.run_until_complete(main())
            except (KeyboardInterrupt, SystemExit):
                # Normal termination, exit the loop
                print("Bot stopped by user.")
                break
            except ValueError as e:
                # This error is from the FloodWait parsing issue
                print(f"Value error detected: {e}")
                print("This is likely due to a Telegram flood wait. Waiting for 10 minutes...")
                # Set a long timeout for flood wait
                time.sleep(600)  # 10 minutes
                print("Restarting bot...")
                continue
            except Exception as e:
                # Any other exception, log and restart
                print(f"Critical error detected: {e}")
                print(f"Bot crashed. Restarting in 10 seconds...")
                traceback.print_exc()
                time.sleep(10)
                print("Restarting bot...")
                continue
    
    # Start bot with automatic restart capability
    run_bot_with_restart()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01