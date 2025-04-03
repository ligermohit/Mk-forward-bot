# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from os import environ 

class Config:
    # Get the raw values from environment
    env_api_id = environ.get("API_ID", "26205052")
    env_api_hash = environ.get("API_HASH", "5425d539963c1b371728c9003a94118f")
    
    # Check if values are swapped (API_ID contains hex string and API_HASH contains digits)
    if (len(env_api_id) >= 32 and all(c in '0123456789abcdef' for c in env_api_id.lower()) and env_api_hash.isdigit()):
        print("CORRECTION: API_ID and API_HASH values are swapped in environment variables.")
        # Use swapped values
        API_ID = int(env_api_hash)  # API_ID should be numeric
        API_HASH = env_api_id       # API_HASH should be hex string
        print(f"Using API_ID: {API_ID}")
        print(f"Using API_HASH: {API_HASH[:5]}...{API_HASH[-5:]}")  # Only show part of hash for security
    else:
        # Try to use values as is with fallback to empty values for GitHub
        try:
            API_ID = int(env_api_id) if env_api_id else 0
        except ValueError:
            API_ID = 0
            
        # For API_HASH, prefer env value unless it's clearly wrong (numeric)
        if env_api_hash and not env_api_hash.isdigit():
            API_HASH = env_api_hash
        else:
            # If env_api_id looks like a hash, use it instead
            if len(env_api_id) >= 32 and all(c in '0123456789abcdef' for c in env_api_id.lower()):
                API_HASH = env_api_id
            else:
                # If we don't have a valid API_HASH, log error
                print("ERROR: No valid API_HASH found in environment variables.")
                API_HASH = ""
    BOT_TOKEN = environ.get("BOT_TOKEN", "") 
    BOT_SESSION = environ.get("BOT_SESSION", "vjbot_new") 
    DATABASE_URI = environ.get("MONGODB_URI", "mongodb+srv://Forward-Bot:xn6grl70Ppsb0l3p@forward-bot.ks9zzxi.mongodb.net/?retryWrites=true&w=majority&appName=Forward-Bot")
    DATABASE_NAME = environ.get("DATABASE_NAME", "Forward-Bot")
    # Handle BOT_OWNER with proper error handling
    try:
        primary_owner = int(environ.get("BOT_OWNER", "7404299810"))
        BOT_OWNER = primary_owner  # Set primary owner as the main BOT_OWNER for equality checks
        BOT_OWNERS = [primary_owner, 6552970915]  # List of all bot owners
        print(f"BOT_OWNER set to: {BOT_OWNER}")
    except ValueError:
        print("WARNING: BOT_OWNER should be a number! Using default value.")
        BOT_OWNER = 7404299810
        BOT_OWNERS = [7404299810, 6552970915]
    # Handle LOG_CHANNEL with proper error handling
    try:
        LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002276790456"))  # Channel for logging activities
    except ValueError:
        print("WARNING: LOG_CHANNEL should be a valid integer! Using default value.")
        LOG_CHANNEL = -1002276790456
    
    # Channel ID for forced subscription with error handling
    try:
        FORCE_CHANNEL_ID = int(environ.get("FORCE_CHANNEL_ID", "-1002521003950"))
    except ValueError:
        print("WARNING: FORCE_CHANNEL_ID should be a valid integer! Using default value.")
        FORCE_CHANNEL_ID = -1002521003950 
    # Channel username without '@' - used for public channels or fallback for private channels
    FORCE_CHANNEL_USERNAME = environ.get("FORCE_CHANNEL_USERNAME", "iCrunchkornBots")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    # Default speed settings (sleep time in seconds between messages)
    # These values represent message forwarding speeds:
    # 3.0 seconds = ~20 messages per minute
    # 1.2 seconds = ~50 messages per minute
    BOT_FORWARD_SPEED = float(environ.get("BOT_FORWARD_SPEED", "2.0"))    # Default bot forward speed (~30 messages per minute)
    USERBOT_FORWARD_SPEED = float(environ.get("USERBOT_FORWARD_SPEED", "1.2"))  # Default userbot forward speed (~30 messages per minute)
    
    # Speed limits (messages per minute)
    MIN_FORWARD_SPEED = 20  # Minimum 20 messages per minute (3.0 seconds delay)
    MAX_FORWARD_SPEED = 50  # Maximum 50 messages per minute (1.2 seconds delay)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
