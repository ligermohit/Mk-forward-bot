# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import sys
import asyncio 
from database import Db, db
from config import Config, temp
from script import Script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument, CallbackQuery
from pyrogram.errors import UserNotParticipant
import psutil
import time as time
from os import environ, execle, system

START_TIME = time.time()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

main_buttons = [[
    InlineKeyboardButton('❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ ❣️', url='https://t.me/+Ut3lLSDKlEMyNjI1')
],[
    InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/MoviesRequest_iKorn'),
    InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/iCrunchkornBots')
],[
    InlineKeyboardButton('🤖 ᴀʙᴏᴜᴛ ʙᴏᴛ', callback_data='help'),
    InlineKeyboardButton('💁 ᴀʙᴏᴜᴛ', callback_data='about')
],[
    InlineKeyboardButton('⚙ sᴇᴛᴛɪɴɢs', callback_data='settings#main')
]]

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Helper function to check if a user is a member of the channel
async def is_subscribed(client, user_id):
    try:
        # First check if the channel exists and is accessible
        try:
            # Just get basic info about the channel to ensure it exists
            channel = await client.get_chat(Config.FORCE_CHANNEL_ID)
            print(f"Successfully connected to channel: {channel.title}")
        except Exception as ce:
            print(f"Channel access error: {ce} - Bypassing subscription check")
            # If we can't access the channel, don't force subscription
            return True
            
        # Now check if user is subscribed to the channel
        member = await client.get_chat_member(Config.FORCE_CHANNEL_ID, user_id)
        return True
    except UserNotParticipant:
        # User is not a member of the channel
        return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        # In case of error, we'll allow the user to proceed
        return True

# Function to create an invite link for private channels
async def create_channel_invite_link(client):
    try:
        # Check if the channel is private and create an invite link
        chat = await client.get_chat(Config.FORCE_CHANNEL_ID)
        
        # If it's a private channel, create an invite link
        if chat.type == "channel" and (chat.username is None or chat.username == ""):
            invite_link = await client.create_chat_invite_link(
                chat_id=Config.FORCE_CHANNEL_ID,
                creates_join_request=False,  # Direct join without admin approval
                member_limit=1,  # One-time use link
                expire_date=None  # No expiration
            )
            return invite_link.invite_link
        # For public channels, use the username
        elif chat.username:
            return f"https://t.me/{chat.username}"
        else:
            # Fallback to default username if we can't create a link
            return f"https://t.me/{Config.FORCE_CHANNEL_USERNAME}"
    except Exception as e:
        print(f"Error creating invite link: {e}")
        # Fallback to default username if there's an error
        return f"https://t.me/{Config.FORCE_CHANNEL_USERNAME}"

@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    
    # First check if the user is banned
    from database import db
    
    try:
        ban_status = await db.get_ban_status(user.id)
        
        if ban_status and ban_status.get('is_banned', False):
            # User is banned, send ban message and stop processing
            await message.reply_text(
                "<b>⚠️ Your account has been banned from using this bot.</b>\n\n"
                "<b>If you believe this is an error, please contact the administrator.</b>"
            )
            # Stop further processing of this message
            return
    except Exception as e:
        print(f"Error checking ban status in start command: {e}")
        # Continue processing even if there's an error checking ban status
    
    # Add error handling for database operations
    try:
        # Check if user exists and add if not
        if not await db.is_user_exist(user.id):
            try:
                await db.add_user(user.id, user.first_name)
                print(f"Added new user: {user.id} - {user.first_name}")
            except Exception as e:
                print(f"Error adding user to database: {e}")
    except Exception as e:
        print(f"Database error checking user existence: {e}")
    
    # Try to check channel subscription with error handling
    try:
        is_member = await is_subscribed(client, user.id)
    except Exception as e:
        print(f"Error checking subscription: {e}")
        # Default to allowing access if we can't check subscription
        is_member = True
    
    if is_member:
        # First send the sticker
        try:
            sticker_message = await client.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgQAAxkBAAEHL0Zn692WuHikouqtYBoqgwZnWFqkCQACBxEAAvdksVLSCRrlNPhFZh4E"
            )
            
            # Wait for 1 second and then delete the sticker
            await asyncio.sleep(1)
            await sticker_message.delete()
            
            # Then send the normal welcome message with photo
            reply_markup = InlineKeyboardMarkup(main_buttons)
            try:
                # Send the image with caption
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo="static/bot_image.jpg", 
                    caption=Script.START_TXT.format(message.from_user.first_name),
                    reply_markup=reply_markup
                )
            except Exception as e:
                # Fallback to text-only if photo sending fails
                print(f"Error sending photo: {e}")
                await client.send_message(
                    chat_id=message.chat.id,
                    reply_markup=reply_markup,
                    text=Script.START_TXT.format(message.from_user.first_name)
                )
        except Exception as e:
            print(f"Error sending sticker: {e}")
            # If sticker fails, still send the welcome message
            reply_markup = InlineKeyboardMarkup(main_buttons)
            try:
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo="static/bot_image.jpg", 
                    caption=Script.START_TXT.format(message.from_user.first_name),
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await client.send_message(
                    chat_id=message.chat.id,
                    reply_markup=reply_markup,
                    text=Script.START_TXT.format(message.from_user.first_name)
                )
    else:
        # If user is not a member, create or get channel invite link
        channel_link = await create_channel_invite_link(client)
        
        buttons = [
            [InlineKeyboardButton("📢 Join Channel", url=channel_link)],
            [InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            chat_id=message.chat.id,
            text=Script.FORCE_SUB_TXT.format(message.from_user.first_name),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER))
async def restart(client, message):
    msg = await message.reply_text(text="<i>Trying to restarting.....</i>")
    await asyncio.sleep(5)
    await msg.edit("<i>Server restarted successfully ✅</i>")
    system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
    execle(sys.executable, sys.executable, "main.py", environ)
    
# Helper function to convert seconds delay to messages per minute
def delay_to_msgs_per_min(delay_seconds):
    return int(60 / delay_seconds)

# Helper function to convert messages per minute to seconds delay
def msgs_per_min_to_delay(msgs_per_min):
    return round(60 / msgs_per_min, 1)

# Speed command to adjust bot forwarding speed
@Client.on_message(filters.private & filters.command(['speed']) & filters.user(Config.BOT_OWNER))
async def speed_command(client, message):
    # Create buttons for adjusting bot speed
    bot_current_speed = delay_to_msgs_per_min(temp.BOT_FORWARD_SPEED)
    userbot_current_speed = delay_to_msgs_per_min(temp.USERBOT_FORWARD_SPEED)
    
    buttons = [
        [
            InlineKeyboardButton("🤖 Bot Speed", callback_data="speed_info")
        ],
        [
            InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_bot_minus"),
            InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_bot_plus")
        ],
        [
            InlineKeyboardButton("👤 Userbot Speed", callback_data="speed_info")
        ],
        [
            InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_user_minus"),
            InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_user_plus")
        ],
        [
            InlineKeyboardButton("🔄 Reset to Default", callback_data="speed_reset")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Show current speed settings with messages per minute calculation
    await message.reply_text(
        text=Script.SPEED_TXT.format(
            temp.BOT_FORWARD_SPEED, bot_current_speed,
            temp.USERBOT_FORWARD_SPEED, userbot_current_speed
        ),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^help'))
async def helpcb(bot, query):
    buttons = [[
        InlineKeyboardButton('🤔 ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ❓', callback_data='how_to_use')
    ],[
        InlineKeyboardButton('💎 sᴇᴇ ᴘʟᴀɴs', callback_data='view_plans'),
        InlineKeyboardButton('• back', callback_data='back')
    ],[
        InlineKeyboardButton('📚 ᴄᴏᴍᴍᴀɴᴅs', callback_data='commands')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=Script.HELP_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing help message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.HELP_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in help button: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Help information couldn't be displayed. Please try again or use /help command.</b>",
            reply_markup=reply_markup
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^how_to_use'))
async def how_to_use(bot, query):
    buttons = [[InlineKeyboardButton('• back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=Script.HOW_USE_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing how_to_use message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.HOW_USE_TXT, 
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in how_to_use: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Error displaying usage instructions. Please try again or use /help command.</b>",
            reply_markup=reply_markup
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^back'))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    try:
        # Instead of deleting and sending a new message, let's edit the current message
        # This way, it won't create a new message every time
        try:
            # First try to edit the current message
            await query.message.edit_text(
                text=Script.START_TXT.format(query.from_user.first_name),
                reply_markup=reply_markup
            )
        except Exception as edit_error:
            # If edit fails (e.g. for media messages), then delete and send a photo
            print(f"Error editing message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_photo(
                chat_id=query.message.chat.id,
                photo="static/bot_image.jpg",
                caption=Script.START_TXT.format(query.from_user.first_name),
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error in back button: {e}")
        # Final fallback if all else fails
        await bot.send_message(
            chat_id=query.message.chat.id,
            text=Script.START_TXT.format(query.from_user.first_name),
            reply_markup=reply_markup
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^commands'))
async def commands(bot, query):
    buttons = [[
        InlineKeyboardButton('• back', callback_data='help')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=Script.COMMANDS_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing commands message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.COMMANDS_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in commands button: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Commands information couldn't be displayed. Please try again.</b>",
            reply_markup=reply_markup
        )

@Client.on_callback_query(filters.regex(r'^about'))
async def about(bot, query):
    buttons = [[
         InlineKeyboardButton('• back', callback_data='help'),
         InlineKeyboardButton('Stats ✨️', callback_data='status')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=Script.ABOUT_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing about message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.ABOUT_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in about button: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Error displaying about information. Please try again.</b>",
            reply_markup=reply_markup
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^status'))
async def status(bot, query):
    # Add error handling for database operations
    try:
        users_count, bots_count = await db.total_users_bots_count()
    except Exception as e:
        print(f"Error getting users/bots count: {e}")
        users_count, bots_count = 0, 0
        
    try:
        forwardings = await db.forwad_count()
    except Exception as e:
        print(f"Error getting forwarding count: {e}")
        forwardings = 0
        
    try:
        upt = await get_bot_uptime(START_TIME)
    except Exception as e:
        print(f"Error calculating uptime: {e}")
        upt = "Unknown"
    
    # Check if user is admin
    if query.from_user.id == Config.BOT_OWNER:
        buttons = [[
            InlineKeyboardButton('• back', callback_data='help'),
            InlineKeyboardButton('System Stats ✨️', callback_data='systm_sts'),
        ]]
    else:
        buttons = [[
            InlineKeyboardButton('• back', callback_data='help')
        ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=Script.STATUS_TXT.format(upt, users_count, bots_count, forwardings),
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing status message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.STATUS_TXT.format(upt, users_count, bots_count, forwardings),
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in status button: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Error displaying status information. Please try again.</b>",
            reply_markup=reply_markup
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^systm_sts'))
async def sys_status(bot, query):
    # Check if user is admin, if not send unauthorized message
    if query.from_user.id != Config.BOT_OWNER:
        await query.answer("You are not authorized to view system stats.", show_alert=True)
        return
        
    buttons = [[InlineKeyboardButton('• back', callback_data='help')]]
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()
    disk_usage = psutil.disk_usage('/')
    total_space = disk_usage.total / (1024**3)  # Convert to GB
    used_space = disk_usage.used / (1024**3)    # Convert to GB
    free_space = disk_usage.free / (1024**3)
    text = f"""
╔════❰ sᴇʀᴠᴇʀ sᴛᴀᴛs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ <b>ᴛᴏᴛᴀʟ ᴅɪsᴋ sᴘᴀᴄᴇ</b>: <code>{total_space:.2f} GB</code>
║┣⪼ <b>ᴜsᴇᴅ</b>: <code>{used_space:.2f} GB</code>
║┣⪼ <b>ꜰʀᴇᴇ</b>: <code>{free_space:.2f} GB</code>
║┣⪼ <b>ᴄᴘᴜ</b>: <code>{cpu}%</code>
║┣⪼ <b>ʀᴀᴍ</b>: <code>{ram}%</code>
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
"""
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing system stats message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in system status button: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Error displaying system stats. Please try again.</b>",
            reply_markup=reply_markup
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def get_bot_uptime(start_time):
    # Calculate the uptime in seconds
    uptime_seconds = int(time.time() - start_time)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_weeks = uptime_days // 7
    uptime_string = ""
    if uptime_hours != 0:
        uptime_string += f" {uptime_hours % 24}H"
    if uptime_minutes != 0:
        uptime_string += f" {uptime_minutes % 60}M"
    uptime_string += f" {uptime_seconds % 60} Sec"
    return uptime_string   

# Handler for "check_subscription" callback button
@Client.on_callback_query(filters.regex(r'^check_subscription'))
async def check_subscription(bot, query):
    user_id = query.from_user.id
    is_member = await is_subscribed(bot, user_id)
    
    if is_member:
        # User has joined the channel, show welcome message with photo
        reply_markup = InlineKeyboardMarkup(main_buttons)
        try:
            # Delete current message and send a new photo message (for home page always use image)
            await query.message.delete()            
            # Send a new photo
            await bot.send_photo(
                chat_id=query.message.chat.id,
                photo="static/bot_image.jpg",
                caption=Script.START_TXT.format(query.from_user.first_name),
                reply_markup=reply_markup
            )
            # Show a quick "Successfully joined!" notification
            await query.answer("✅ You've successfully joined the channel!", show_alert=False)
        except Exception as e:
            print(f"Error in check_subscription for member: {e}")
            # Last resort fallback
            await bot.send_message(
                chat_id=query.message.chat.id,
                reply_markup=reply_markup,
                text=Script.START_TXT.format(query.from_user.first_name)
            )
    else:
        # User still hasn't joined the channel
        # Create or get an invite link for private channels
        channel_link = await create_channel_invite_link(bot)
        
        buttons = [
            [InlineKeyboardButton("📢 Join Channel", url=channel_link)],
            [InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.answer("You need to join the channel first!", show_alert=True)
        
        # Update the message with the same force subscription text
        try:
            await query.message.edit_text(
                text=Script.FORCE_SUB_TXT.format(query.from_user.first_name),
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"Error editing force sub message: {e}")
            # If edit fails (rare case), send a new message
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.FORCE_SUB_TXT.format(query.from_user.first_name),
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

# Wrapper function to check subscription
async def check_user_subscription(client, user_id, message=None):
    """
    Check if a user is subscribed to the channel. If not, send a subscription message.
    
    Args:
        client: The bot client
        user_id: User ID to check
        message: Optional message object to reply to
        
    Returns:
        bool: True if user is subscribed, False otherwise
    """
    is_member = await is_subscribed(client, user_id)
    
    if not is_member and message is not None:
        # User is not a member, create or get invite link for the channel
        channel_link = await create_channel_invite_link(client)
        
        buttons = [
            [InlineKeyboardButton("📢 Join Channel", url=channel_link)],
            [InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=Script.FORCE_SUB_TXT.format(message.from_user.first_name),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
    
    return is_member

# Handler for the view_plans callback button
@Client.on_callback_query(filters.regex(r'^view_plans'))
async def view_plans_callback(bot, query):
    buttons = [[
        InlineKeyboardButton('• back', callback_data='help'),
    ], [
        InlineKeyboardButton('💰 Contact Admin', url=f'https://t.me/itz_THANOS')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        # Try to edit the current message first
        try:
            await query.message.edit_text(
                text=Script.PLANS_INFO_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as edit_error:
            # If edit fails, then delete and send a new message
            print(f"Error editing plans message, sending new one: {edit_error}")
            await query.message.delete()
            await bot.send_message(
                chat_id=query.message.chat.id,
                text=Script.PLANS_INFO_TXT,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Error in view_plans callback: {e}")
        # Last resort fallback
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="<b>Error displaying plan information. Please try using /plans command instead.</b>",
            reply_markup=reply_markup
        )

# Callbacks for speed adjustment buttons
@Client.on_callback_query(filters.regex(r'^speed_bot_(plus|minus)'))
async def speed_bot_callback(bot, query):
    # Only allow bot owner to change speed settings
    if query.from_user.id != Config.BOT_OWNER:
        return await query.answer("You are not authorized to change speed settings.", show_alert=True)
    
    # Get current speed in messages per minute
    current_speed_msgs = delay_to_msgs_per_min(temp.BOT_FORWARD_SPEED)
    
    # Determine action (plus or minus)
    action = query.data.split('_')[2]
    
    # Adjust speed by 5 messages per minute
    if action == "plus":
        # Increase speed by 5 msgs/min (reduce delay)
        new_speed_msgs = min(current_speed_msgs + 5, temp.MAX_FORWARD_SPEED)
    else:  # minus
        # Decrease speed by 5 msgs/min (increase delay)
        new_speed_msgs = max(current_speed_msgs - 5, temp.MIN_FORWARD_SPEED)
    
    # Convert back to seconds delay
    new_delay = msgs_per_min_to_delay(new_speed_msgs)
    temp.BOT_FORWARD_SPEED = new_delay
    
    try:
        # Show success message
        await query.answer(f"Bot speed: {new_speed_msgs} msgs/min ({new_delay}s delay)", show_alert=True)
        
        # Get userbot speed for display
        userbot_speed_msgs = delay_to_msgs_per_min(temp.USERBOT_FORWARD_SPEED)
        
        # Update the message with new speed settings
        buttons = [
            [
                InlineKeyboardButton("🤖 Bot Speed", callback_data="speed_info")
            ],
            [
                InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_bot_minus"),
                InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_bot_plus")
            ],
            [
                InlineKeyboardButton("👤 Userbot Speed", callback_data="speed_info")
            ],
            [
                InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_user_minus"),
                InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_user_plus")
            ],
            [
                InlineKeyboardButton("🔄 Reset to Default", callback_data="speed_reset")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_text(
            text=Script.SPEED_TXT.format(
                temp.BOT_FORWARD_SPEED, new_speed_msgs,
                temp.USERBOT_FORWARD_SPEED, userbot_speed_msgs
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in speed_bot_callback: {e}")
        await query.answer("Failed to update speed settings. Please try again.", show_alert=True)

# Callback for userbot speed adjustment buttons
@Client.on_callback_query(filters.regex(r'^speed_user_(plus|minus)'))
async def speed_user_callback(bot, query):
    # Only allow bot owner to change speed settings
    if query.from_user.id != Config.BOT_OWNER:
        return await query.answer("You are not authorized to change speed settings.", show_alert=True)
    
    # Get current speed in messages per minute
    current_speed_msgs = delay_to_msgs_per_min(temp.USERBOT_FORWARD_SPEED)
    
    # Determine action (plus or minus)
    action = query.data.split('_')[2]
    
    # Adjust speed by 5 messages per minute
    if action == "plus":
        # Increase speed by 5 msgs/min (reduce delay)
        new_speed_msgs = min(current_speed_msgs + 5, temp.MAX_FORWARD_SPEED)
    else:  # minus
        # Decrease speed by 5 msgs/min (increase delay)
        new_speed_msgs = max(current_speed_msgs - 5, temp.MIN_FORWARD_SPEED)
    
    # Convert back to seconds delay
    new_delay = msgs_per_min_to_delay(new_speed_msgs)
    temp.USERBOT_FORWARD_SPEED = new_delay
    
    try:
        # Show success message
        await query.answer(f"Userbot speed: {new_speed_msgs} msgs/min ({new_delay}s delay)", show_alert=True)
        
        # Get bot speed for display
        bot_speed_msgs = delay_to_msgs_per_min(temp.BOT_FORWARD_SPEED)
        
        # Update the message with new speed settings
        buttons = [
            [
                InlineKeyboardButton("🤖 Bot Speed", callback_data="speed_info")
            ],
            [
                InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_bot_minus"),
                InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_bot_plus")
            ],
            [
                InlineKeyboardButton("👤 Userbot Speed", callback_data="speed_info")
            ],
            [
                InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_user_minus"),
                InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_user_plus")
            ],
            [
                InlineKeyboardButton("🔄 Reset to Default", callback_data="speed_reset")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_text(
            text=Script.SPEED_TXT.format(
                temp.BOT_FORWARD_SPEED, bot_speed_msgs,
                temp.USERBOT_FORWARD_SPEED, new_speed_msgs
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in speed_user_callback: {e}")
        await query.answer("Failed to update speed settings. Please try again.", show_alert=True)

# Speed info handler (no action)
@Client.on_callback_query(filters.regex(r'^speed_info'))
async def speed_info_callback(bot, query):
    await query.answer("This is just an info label, not a button", show_alert=False)

# Speed reset handler
@Client.on_callback_query(filters.regex(r'^speed_reset'))
async def speed_reset_callback(bot, query):
    # Only allow bot owner to change speed settings
    if query.from_user.id != Config.BOT_OWNER:
        return await query.answer("You are not authorized to change speed settings.", show_alert=True)
    
    # Reset to default values (2.0 seconds = ~30 msgs/min)
    temp.BOT_FORWARD_SPEED = 2.0
    temp.USERBOT_FORWARD_SPEED = 2.0
    
    # Calculate messages per minute
    bot_speed_msgs = delay_to_msgs_per_min(temp.BOT_FORWARD_SPEED)
    userbot_speed_msgs = delay_to_msgs_per_min(temp.USERBOT_FORWARD_SPEED)
    
    try:
        # Show success message
        await query.answer("Speed settings reset to default values", show_alert=True)
        
        # Update the message with reset speed settings
        buttons = [
            [
                InlineKeyboardButton("🤖 Bot Speed", callback_data="speed_info")
            ],
            [
                InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_bot_minus"),
                InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_bot_plus")
            ],
            [
                InlineKeyboardButton("👤 Userbot Speed", callback_data="speed_info")
            ],
            [
                InlineKeyboardButton("➖ Slower (-5)", callback_data="speed_user_minus"),
                InlineKeyboardButton("➕ Faster (+5)", callback_data="speed_user_plus")
            ],
            [
                InlineKeyboardButton("🔄 Reset to Default", callback_data="speed_reset")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_text(
            text=Script.SPEED_TXT.format(
                temp.BOT_FORWARD_SPEED, bot_speed_msgs,
                temp.USERBOT_FORWARD_SPEED, userbot_speed_msgs
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in speed_reset_callback: {e}")
        await query.answer("Failed to reset speed settings. Please try again.", show_alert=True)

# Close button handler
@Client.on_callback_query(filters.regex(r'^close'))
async def close_callback(bot, query):
    try:
        await query.message.delete()
        await query.answer("Closed")
    except Exception as e:
        print(f"Error in close callback: {e}")
        await query.answer("Failed to close. Please try again.")

# Middleware to check if user is banned - runs before any other middleware
@Client.on_message(filters.private & ~filters.user(Config.BOT_OWNER))
async def banned_user_middleware(client, message):
    # Check if user is banned
    from database import db
    
    try:
        user_id = message.from_user.id
        ban_status = await db.get_ban_status(user_id)
        
        if ban_status and ban_status.get('is_banned', False):
            # User is banned, send ban message and stop processing
            await message.reply_text(
                "<b>⚠️ Your account has been banned from using this bot.</b>\n\n"
                "<b>If you believe this is an error, please contact the administrator.</b>"
            )
            # Stop further processing of this message
            return True
    except Exception as e:
        print(f"Error checking ban status: {e}")
        # In case of error, allow the message to be processed
        pass
    
    # User is not banned, continue processing
    return False

# Middleware to check channel membership for commands except essential ones
@Client.on_message(filters.private & ~filters.command(['start', 'help', 'myplan', 'plans']) & ~filters.user(Config.BOT_OWNER))
async def force_sub_middleware(client, message):
    # First check if the user is banned
    is_banned = await banned_user_middleware(client, message)
    if is_banned:
        # User is banned, stop processing
        return
        
    # Skip middleware for essential commands to make them always available
    if message.command and message.command[0] in ['forward']:
        # Only check subscription before starting forwarding process
        user = message.from_user
        is_member = await check_user_subscription(client, user.id, message)
        
        if not is_member:
            # If user is not a channel member, stop processing
            return
    # For all other commands that aren't excluded, continue normally
    return

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
