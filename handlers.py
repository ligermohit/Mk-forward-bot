import logging
import time
from typing import List, Dict, Any
from telegram import Update, Bot
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from database import (
    add_source_channel,
    add_destination_channel,
    get_source_channels,
    get_destination_channels,
    remove_source_channel,
    remove_destination_channel,
    save_forwarded_message
)
from utils import is_admin, extract_channel_id, get_last_processed_message_id

logger = logging.getLogger(__name__)

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "Welcome to the Telegram Forward Bot!\n"
        "Use /help to see available commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/add_source <channel_id or @username> - Add a source channel\n"
        "/add_destination <channel_id or @username> - Add a destination channel\n"
        "/remove_source <channel_id or @username> - Remove a source channel\n"
        "/remove_destination <channel_id or @username> - Remove a destination channel\n"
        "/list - List all configured source and destination channels\n"
        "/status - Check bot status\n\n"
        "Note: The bot must be a member of all source and destination channels."
    )
    await update.message.reply_text(help_text)

async def add_source_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /add_source command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a channel ID or username.")
        return
    
    channel = context.args[0]
    channel_id = extract_channel_id(channel)
    
    try:
        # Verify the channel exists and bot has access
        chat = await context.bot.get_chat(channel_id)
        add_source_channel(chat.id)
        await update.message.reply_text(f"Added {chat.title} ({chat.id}) as a source channel.")
    except TelegramError as e:
        logger.error(f"Error adding source channel {channel_id}: {e}")
        await update.message.reply_text(f"Error: {e}. Make sure the bot is a member of the channel.")

async def add_destination_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /add_destination command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a channel ID or username.")
        return
    
    channel = context.args[0]
    channel_id = extract_channel_id(channel)
    
    try:
        # Verify the channel exists and bot has access
        chat = await context.bot.get_chat(channel_id)
        add_destination_channel(chat.id)
        await update.message.reply_text(f"Added {chat.title} ({chat.id}) as a destination channel.")
    except TelegramError as e:
        logger.error(f"Error adding destination channel {channel_id}: {e}")
        await update.message.reply_text(f"Error: {e}. Make sure the bot is a member of the channel.")

async def remove_source_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /remove_source command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a channel ID or username.")
        return
    
    channel = context.args[0]
    channel_id = extract_channel_id(channel)
    
    if remove_source_channel(channel_id):
        await update.message.reply_text(f"Removed {channel_id} from source channels.")
    else:
        await update.message.reply_text(f"Channel {channel_id} was not found in source channels.")

async def remove_destination_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /remove_destination command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a channel ID or username.")
        return
    
    channel = context.args[0]
    channel_id = extract_channel_id(channel)
    
    if remove_destination_channel(channel_id):
        await update.message.reply_text(f"Removed {channel_id} from destination channels.")
    else:
        await update.message.reply_text(f"Channel {channel_id} was not found in destination channels.")

async def list_config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /list command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    source_channels = get_source_channels()
    destination_channels = get_destination_channels()
    
    message = "Current configuration:\n\n"
    
    if source_channels:
        message += "Source channels:\n"
        for channel in source_channels:
            try:
                chat = await context.bot.get_chat(channel)
                message += f"- {chat.title} ({chat.id})\n"
            except TelegramError:
                message += f"- {channel} (Unable to get channel info)\n"
    else:
        message += "No source channels configured.\n"
    
    message += "\n"
    
    if destination_channels:
        message += "Destination channels:\n"
        for channel in destination_channels:
            try:
                chat = await context.bot.get_chat(channel)
                message += f"- {chat.title} ({chat.id})\n"
            except TelegramError:
                message += f"- {channel} (Unable to get channel info)\n"
    else:
        message += "No destination channels configured.\n"
    
    await update.message.reply_text(message)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    if not is_admin(update.effective_user.id, context):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    source_channels = get_source_channels()
    destination_channels = get_destination_channels()
    
    status = "Bot Status:\n\n"
    status += f"✅ Bot is running\n"
    status += f"📊 Source channels: {len(source_channels)}\n"
    status += f"📊 Destination channels: {len(destination_channels)}\n"
    
    await update.message.reply_text(status)

async def forward_message(bot: Bot, source_channel_id: str, destination_channels: List[str], config: Dict[str, Any]) -> None:
    """
    Forward messages from a source channel to destination channels.
    
    Args:
        bot: The Telegram bot instance
        source_channel_id: The source channel ID
        destination_channels: List of destination channel IDs
        config: Bot configuration dictionary
    """
    try:
        # Get last processed message ID for this source
        last_message_id = get_last_processed_message_id(source_channel_id)
        
        # Get messages from the source channel
        messages = []
        try:
            # Get the last 100 messages from the channel
            # We'll filter out already processed ones later
            messages = await bot.get_chat_history(
                chat_id=source_channel_id,
                limit=100
            )
        except AttributeError:
            # Fallback for older telegram-bot versions that don't have get_chat_history
            logger.warning("get_chat_history not available, using get_updates instead")
            updates = await bot.get_updates(offset=-100, allowed_updates=["channel_post"])
            for update in updates:
                if update.channel_post and str(update.channel_post.chat.id) == str(source_channel_id):
                    messages.append(update.channel_post)
        
        # Filter out already processed messages
        new_messages = [msg for msg in messages if msg.message_id > last_message_id]
        
        if not new_messages:
            logger.debug(f"No new messages in source channel {source_channel_id}")
            return
        
        logger.info(f"Found {len(new_messages)} new messages in source channel {source_channel_id}")
        
        # Sort messages by message_id to forward in correct order
        new_messages.sort(key=lambda msg: msg.message_id)
        
        for message in new_messages:
            # Forward to all destination channels
            for dest_channel in destination_channels:
                try:
                    # Forward differently based on message type
                    if message.text:
                        await bot.send_message(
                            chat_id=dest_channel,
                            text=message.text,
                            disable_web_page_preview=False
                        )
                    elif message.photo and config["forward_media"]:
                        # Get the largest photo
                        photo = message.photo[-1]
                        caption = message.caption if config["include_captions"] and message.caption else None
                        await bot.send_photo(
                            chat_id=dest_channel,
                            photo=photo.file_id,
                            caption=caption
                        )
                    elif message.video and config["forward_media"]:
                        caption = message.caption if config["include_captions"] and message.caption else None
                        await bot.send_video(
                            chat_id=dest_channel,
                            video=message.video.file_id,
                            caption=caption
                        )
                    elif message.document and config["forward_media"]:
                        caption = message.caption if config["include_captions"] and message.caption else None
                        await bot.send_document(
                            chat_id=dest_channel,
                            document=message.document.file_id,
                            caption=caption
                        )
                    elif message.audio and config["forward_media"]:
                        caption = message.caption if config["include_captions"] and message.caption else None
                        await bot.send_audio(
                            chat_id=dest_channel,
                            audio=message.audio.file_id,
                            caption=caption
                        )
                    elif message.voice and config["forward_media"]:
                        caption = message.caption if config["include_captions"] and message.caption else None
                        await bot.send_voice(
                            chat_id=dest_channel,
                            voice=message.voice.file_id,
                            caption=caption
                        )
                    # Add more types as needed
                    
                    logger.info(f"Forwarded message {message.message_id} from {source_channel_id} to {dest_channel}")
                    # Add a small delay to avoid hitting rate limits
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error forwarding message {message.message_id} to {dest_channel}: {e}")
            
            # Save the last processed message ID for this source
            save_forwarded_message(source_channel_id, message.message_id)
            
    except Exception as e:
        logger.error(f"Error in forward_message for source {source_channel_id}: {e}")
