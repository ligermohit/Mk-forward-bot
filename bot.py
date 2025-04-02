import logging
import time
from typing import Dict, Any
import telegram
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from handlers import (
    start_command,
    help_command,
    add_source_command,
    add_destination_command,
    list_config_command,
    remove_source_command,
    remove_destination_command,
    status_command,
    forward_message
)
from database import init_db

logger = logging.getLogger(__name__)

def create_bot(config: Dict[str, Any]) -> telegram.ext.Application:
    """
    Create and configure the Telegram bot.
    
    Args:
        config: Bot configuration dictionary
    
    Returns:
        Application: Configured Telegram bot instance
    """
    logger.info("Initializing bot...")
    
    # Initialize the database
    init_db(config["db_path"])
    
    # Create the Application
    application = ApplicationBuilder().token(config["token"]).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_source", add_source_command))
    application.add_handler(CommandHandler("add_destination", add_destination_command))
    application.add_handler(CommandHandler("list", list_config_command))
    application.add_handler(CommandHandler("remove_source", remove_source_command))
    application.add_handler(CommandHandler("remove_destination", remove_destination_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    logger.info("Bot initialization complete")
    return application

async def error_handler(update: object, context: CallbackContext) -> None:
    """
    Error handler for the Telegram bot.
    
    Args:
        update: The update object
        context: The context object
    """
    logger.error(f"Update {update} caused error: {context.error}")

async def process_updates(application: telegram.ext.Application, config: Dict[str, Any]) -> None:
    """
    Process updates from source channels and forward them to destination channels.
    
    Args:
        application: The Telegram bot application
        config: Bot configuration dictionary
    """
    from database import get_source_channels, get_destination_channels
    
    source_channels = get_source_channels()
    destination_channels = get_destination_channels()
    
    # If no channels are configured in the database, use the ones from config
    if not source_channels and config["source_channels"]:
        source_channels = config["source_channels"]
    
    if not destination_channels and config["destination_channels"]:
        destination_channels = config["destination_channels"]
    
    if not source_channels or not destination_channels:
        logger.warning("No source or destination channels configured. Waiting...")
        return
    
    try:
        logger.debug(f"Checking for updates from source channels: {source_channels}")
        # For each source channel, get the latest messages and forward them
        for source in source_channels:
            await forward_message(application.bot, source, destination_channels, config)
    except Exception as e:
        logger.error(f"Error while processing updates: {e}")

def start_bot(application: telegram.ext.Application, config: Dict[str, Any]) -> None:
    """
    Start the Telegram bot and polling loop.
    
    Args:
        application: The Telegram bot application
        config: Bot configuration dictionary
    """
    import asyncio
    
    async def polling_loop():
        """Background task to periodically check for updates to forward"""
        while True:
            try:
                await process_updates(application, config)
                await asyncio.sleep(config["polling_interval"])
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(30)  # Longer delay on error
    
    # Start the background polling task
    loop = asyncio.get_event_loop()
    loop.create_task(polling_loop())
    
    logger.info("Starting bot...")
    application.run_polling()
