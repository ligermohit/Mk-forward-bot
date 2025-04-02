import asyncio
import datetime
import pytz
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from script import Script
# Will import app in runtime to avoid circular import

# Add a standalone version for direct text messages
async def log_to_channel(message_text, client=None):
    """
    Send a text message to the log channel.
    This simpler version is for direct text messages from anywhere in the app.
    
    Args:
        message_text: The text message to log
        client: Optional client to use, if not provided tries to import from main
    """
    try:
        if not Config.LOG_CHANNEL:
            return
            
        # Use provided client or try to import from main (may fail if circular import)
        bot_client = client
        if not bot_client:
            try:
                from main import app
                bot_client = app
            except ImportError:
                print("Warning: Could not import app from main, logging may fail without client")
        
        # Get IST time
        ist_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.datetime.now(ist_tz).strftime("%d-%m-%Y %H:%M:%S")
        
        # Add timestamp to message if it doesn't already have one
        if "<b>⌖ Time:</b>" not in message_text:
            message_text += f"\n<b>⌖ Time:</b> {current_time}"
        
        await bot_client.send_message(
            chat_id=Config.LOG_CHANNEL,
            text=message_text,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in logging text to channel: {e}")

async def log_structured_message(client, message_type, details=None, user_info=None):
    """
    Send structured log messages to the configured log channel
    
    Args:
        client: The bot client
        message_type: Type of log message (new_user, new_bot, premium, forwarding)
        details: Additional details specific to the message type
        user_info: Info about the user involved
    """
    try:
        if not Config.LOG_CHANNEL:
            return
            
        # Use provided client or try to import from main
        bot_client = client
        if not bot_client:
            try:
                from main import app
                bot_client = app
            except ImportError:
                print("Warning: Could not import app from main, logging may fail without client")
            
        # Get IST time
        ist_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.datetime.now(ist_tz).strftime("%d-%m-%Y %H:%M:%S")
        
        if message_type == "new_user":
            user_id = user_info.get("id")
            name = user_info.get("name")
            username = user_info.get("username", "None")
            
            text = f"""<b>💫 NEW USER JOINED 💫</b>

<b>⌖ User:</b> <a href='tg://user?id={user_id}'>{name}</a>
<b>⌖ ID:</b> <code>{user_id}</code>
<b>⌖ Username:</b> @{username}
<b>⌖ Time:</b> {current_time}

<b>🤖 Total Users:</b> <code>{details['total_users']}</code>"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
        elif message_type == "new_bot":
            user_id = user_info.get("id")
            name = user_info.get("name")
            bot_details = details.get("bot_details", {})
            
            text = f"""<b>🤖 NEW BOT ADDED 🤖</b>

<b>⌖ Owner:</b> <a href='tg://user?id={user_id}'>{name}</a>
<b>⌖ Owner ID:</b> <code>{user_id}</code>
<b>⌖ Bot Name:</b> <code>{bot_details.get('name', 'Unknown')}</code>
<b>⌖ Bot Username:</b> @{bot_details.get('username', 'Unknown')}
<b>⌖ Bot ID:</b> <code>{bot_details.get('id', 'Unknown')}</code>
<b>⌖ Time:</b> {current_time}"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
        elif message_type == "premium":
            user_id = user_info.get("id")
            name = user_info.get("name")
            plan_details = details.get("plan_details", {})
            
            text = f"""<b>💎 NEW PREMIUM ACTIVATION 💎</b>

<b>⌖ User:</b> <a href='tg://user?id={user_id}'>{name}</a>
<b>⌖ ID:</b> <code>{user_id}</code>
<b>⌖ Plan:</b> <code>{plan_details.get('plan_name', 'Unknown')}</code>
<b>⌖ Daily Limit:</b> <code>{plan_details.get('daily_limit', 'Unknown')} files</code>
<b>⌖ Expires:</b> <code>{plan_details.get('expiry', 'Unknown')}</code>
<b>⌖ Time:</b> {current_time}"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
        elif message_type == "forwarding_start":
            user_id = user_info.get("id")
            name = user_info.get("name")
            forward_details = details.get("forward_details", {})
            
            text = f"""<b>🔄 FORWARDING STARTED 🔄</b>

<b>⌖ User:</b> <a href='tg://user?id={user_id}'>{name}</a>
<b>⌖ ID:</b> <code>{user_id}</code>
<b>⌖ From Chat:</b> <code>{forward_details.get('from_chat', 'Unknown')}</code>
<b>⌖ To Chat:</b> <code>{forward_details.get('to_chat', 'Unknown')}</code>
<b>⌖ Start ID:</b> <code>{forward_details.get('start_id', 'Unknown')}</code>
<b>⌖ End ID:</b> <code>{forward_details.get('end_id', 'Unknown')}</code>
<b>⌖ Time:</b> {current_time}"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
        elif message_type == "forwarding_complete":
            user_id = user_info.get("id")
            name = user_info.get("name")
            forward_details = details.get("forward_details", {})
            
            text = f"""<b>✅ FORWARDING COMPLETED ✅</b>

<b>⌖ User:</b> <a href='tg://user?id={user_id}'>{name}</a>
<b>⌖ ID:</b> <code>{user_id}</code>
<b>⌖ From Chat:</b> <code>{forward_details.get('from_chat', 'Unknown')}</code>
<b>⌖ To Chat:</b> <code>{forward_details.get('to_chat', 'Unknown')}</code>
<b>⌖ Success:</b> <code>{forward_details.get('success', 0)} files</code>
<b>⌖ Duplicates:</b> <code>{forward_details.get('duplicate', 0)} files</code>
<b>⌖ Failed:</b> <code>{forward_details.get('failed', 0)} files</code>
<b>⌖ Total Time:</b> <code>{forward_details.get('total_time', 'Unknown')}</code>
<b>⌖ Time:</b> {current_time}"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
        elif message_type == "bot_start":
            # Log bot start message
            text = f"""<b>🤖 BOT STARTED 🤖</b>

<b>⌖ Status:</b> <code>Online</code>
<b>⌖ Time:</b> {current_time}
<b>⌖ Version:</b> <code>v0.18.3 (Optimized)</code>
<b>⌖ Mode:</b> <code>24/7 Operation</code>"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
        elif message_type == "keep_alive":
            # Log keep-alive stats
            uptime_details = details or {}
            total_users = uptime_details.get("total_users", "Unknown")
            active_forwards = uptime_details.get("active_forwards", "Unknown")
            check_count = uptime_details.get("check_count", "Unknown")
            
            text = f"""<b>♻️ BOT UPTIME CHECK ♻️</b>

<b>⌖ Status:</b> <code>Running</code>
<b>⌖ Time:</b> {current_time}
<b>⌖ Total Users:</b> <code>{total_users}</code>
<b>⌖ Active Forwards:</b> <code>{active_forwards}</code>
<b>⌖ Check #:</b> <code>{check_count}</code>
<b>⌖ Uptime:</b> <code>Approximately {int(check_count) * 10 if isinstance(check_count, int) else "Unknown"} minutes</code>"""

            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=text,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"Error in logging to channel: {e}")