import re
import logging
from typing import Any, List

logger = logging.getLogger(__name__)

def is_admin(user_id: int, context: Any) -> bool:
    """
    Check if a user is an admin.
    
    Args:
        user_id: User ID to check
        context: Context containing admin IDs
    
    Returns:
        bool: True if user is an admin, False otherwise
    """
    try:
        admin_ids = context.bot_data.get("config", {}).get("admin_ids", [])
        return user_id in admin_ids
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        # Default to deny if there's an error
        return False

def extract_channel_id(channel_input: str) -> str:
    """
    Extract channel ID from user input.
    
    Args:
        channel_input: Channel ID or username
    
    Returns:
        str: Extracted channel ID or original input
    """
    # If it's a numeric ID, return as is
    if channel_input.startswith("-100") and channel_input[4:].isdigit():
        return channel_input
    
    # If it's a username, ensure it has @ prefix
    if not channel_input.startswith("@"):
        channel_input = f"@{channel_input}"
    
    return channel_input

def get_last_processed_message_id(source_channel_id: str) -> int:
    """
    Get the last processed message ID for a source channel.
    
    Args:
        source_channel_id: Source channel ID
    
    Returns:
        int: Last processed message ID or 0 if none
    """
    from database import get_last_processed_message_id as db_get_last
    return db_get_last(source_channel_id)

def format_channel_name(channel_id: str, bot_data: Any) -> str:
    """
    Format a channel name for display.
    
    Args:
        channel_id: Channel ID
        bot_data: Bot data containing channel info
    
    Returns:
        str: Formatted channel name or ID
    """
    channels_info = bot_data.get("channels_info", {})
    channel_info = channels_info.get(channel_id)
    
    if channel_info and channel_info.get("title"):
        return f"{channel_info['title']} ({channel_id})"
    
    return channel_id

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def sanitize_channel_id(channel_id: str) -> str:
    """
    Sanitize a channel ID to ensure it's in the correct format.
    
    Args:
        channel_id: Channel ID to sanitize
    
    Returns:
        str: Sanitized channel ID
    """
    # Remove any whitespace
    channel_id = channel_id.strip()
    
    # If it's a username, ensure it has @ prefix
    if not channel_id.startswith("-") and not channel_id.startswith("@"):
        channel_id = f"@{channel_id}"
    
    return channel_id
