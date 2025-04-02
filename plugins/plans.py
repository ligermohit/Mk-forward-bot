# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import time
import datetime
from database import db
from config import Config
from script import Script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Plan definitions
PLANS = {
    "free": {
        "name": "Free Plan",
        "daily_limit": 100,
        "duration": 0,  # Forever
        "files_limit": 100
    },
    "bronze": {
        "name": "Bronze Plan",
        "daily_limit": 1000,
        "duration": 3 * 24,  # 3 days (in hours)
        "files_limit": 1000
    },
    "silver": {
        "name": "Silver Plan",
        "daily_limit": 1500,
        "duration": 7 * 24,  # 7 days in hours
        "files_limit": 1500
    },
    "gold": {
        "name": "Gold Plan",
        "daily_limit": 3000,
        "duration": 15 * 24,  # 15 days in hours
        "files_limit": 3000
    },
    "diamond": {
        "name": "Diamond Plan",
        "daily_limit": 7777,
        "duration": 30 * 24,  # 30 days in hours
        "files_limit": 7777
    }
}

# Format time remaining in days, hours, minutes, seconds
def format_time_remaining(seconds):
    if seconds <= 0:
        return "Expired"
    
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(days)}d:{int(hours)}h:{int(minutes)}m:{int(seconds)}s"

# Command to check current plan
@Client.on_message(filters.command(["myplan"]) & filters.private)
async def plan_command(client, message):
    # Get user ID directly from the message
    user_id = message.from_user.id
    
    try:
        # First send a response to confirm command was received
        processing_msg = await message.reply_text("Processing your plan information...", quote=True)
        
        # Delete processing message after 1 second
        await asyncio.sleep(1)
        try:
            await processing_msg.delete()
        except Exception as e:
            print(f"Error deleting message: {str(e)}")
            
        # Check if user is the bot owner - special infinity plan
        if user_id == Config.BOT_OWNER:
            # Create special infinity plan message for bot owner
            infinity_message = f"""<b>╔════❰ ʏᴏᴜʀ ᴘʟᴀɴ ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ 🏆 ᴘʟᴀɴ ᴛʏᴘᴇ:</b> <code>Infinity Plan (Owner)</code>
║┃
║┣⪼ <b>⏱️ ᴛɪᴍᴇ ʀᴇᴍᴀɪɴɪɴɢ:</b> <code>∞</code>
║┃
║┣⪼ <b>📊 ᴅᴀɪʟʏ ʟɪᴍɪᴛ:</b> <code>Unlimited</code>
║┃
║┣⪼ <b>📈 ꜰɪʟᴇs ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴛᴏᴅᴀʏ:</b> <code>N/A</code>
║┃
║┣⪼ <b>🔄 ʀᴇᴍᴀɪɴɪɴɢ ꜰɪʟᴇs:</b> <code>Unlimited</code>
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪</b>"""
            
            await message.reply_text(
                infinity_message,
                quote=True
            )
            return
        
        # For normal users - proceed with regular plan checks
        user_plan = await db.get_user_plan(user_id)
        
        if not user_plan:
            # If user has no plan, assign the free plan
            user_plan = {
                "plan_type": "free",
                "plan_name": PLANS["free"]["name"],
                "start_time": time.time(),
                "end_time": 0,  # Never expires for free plan
                "daily_limit": PLANS["free"]["daily_limit"],
                "files_limit": PLANS["free"]["files_limit"],
                "files_forwarded_today": 0,
                "last_day": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            await db.update_user_plan(user_id, user_plan)
        
        # Reset daily counter if it's a new day
        current_day = datetime.datetime.now().strftime("%Y-%m-%d")
        if user_plan.get("last_day") != current_day:
            user_plan["files_forwarded_today"] = 0
            user_plan["last_day"] = current_day
            await db.update_user_plan(user_id, user_plan)
        
        # Format time remaining
        current_time = time.time()
        if user_plan["plan_type"] == "free":
            time_remaining = "∞"  # Infinity symbol for free plan
            remaining_files = user_plan["daily_limit"] - user_plan.get("files_forwarded_today", 0)
        else:
            if user_plan["end_time"] > current_time:
                time_remaining = format_time_remaining(user_plan["end_time"] - current_time)
                remaining_files = user_plan["daily_limit"] - user_plan.get("files_forwarded_today", 0)
            else:
                # Plan expired, assign free plan
                user_plan = {
                    "plan_type": "free",
                    "plan_name": PLANS["free"]["name"],
                    "start_time": time.time(),
                    "end_time": 0,
                    "daily_limit": PLANS["free"]["daily_limit"],
                    "files_limit": PLANS["free"]["files_limit"],
                    "files_forwarded_today": 0,
                    "last_day": current_day
                }
                await db.update_user_plan(user_id, user_plan)
                time_remaining = "∞"
                remaining_files = user_plan["daily_limit"]
        
        # Build plan information message
        message_text = f"""<b>╔════❰ ʏᴏᴜʀ ᴘʟᴀɴ ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ 🏆 ᴘʟᴀɴ ᴛʏᴘᴇ:</b> <code>{user_plan["plan_name"]}</code>
║┃
║┣⪼ <b>⏱️ ᴛɪᴍᴇ ʀᴇᴍᴀɪɴɪɴɢ:</b> <code>{time_remaining}</code>
║┃
║┣⪼ <b>📊 ᴅᴀɪʟʏ ʟɪᴍɪᴛ:</b> <code>{user_plan["daily_limit"]} files</code>
║┃
║┣⪼ <b>📈 ꜰɪʟᴇs ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴛᴏᴅᴀʏ:</b> <code>{user_plan.get("files_forwarded_today", 0)}</code>
║┃
║┣⪼ <b>🔄 ʀᴇᴍᴀɪɴɪɴɢ ꜰɪʟᴇs:</b> <code>{remaining_files}</code>
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪</b>"""

        # Add buttons for premium plans
        buttons = [[
            InlineKeyboardButton('💎 Upgrade to Premium', callback_data='send_plans_command')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(
            message_text,
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        # Handle any exceptions that might occur
        await message.reply_text(f"Error getting plan information: {str(e)}", quote=True)

# Command to show all available plans
@Client.on_message(filters.command("plans") & filters.private)
async def plans_command(client, message):
    try:
        # First send a response to confirm command was received
        processing_msg = await message.reply_text("Loading available plans...", quote=True)
        
        # Delete processing message after 1 second
        await asyncio.sleep(1)
        try:
            await processing_msg.delete()
        except Exception as e:
            print(f"Error deleting message: {str(e)}")
    except Exception as e:
        await message.reply_text(f"Error processing command: {str(e)}", quote=True)
        return
    
    # Build a formatted message with all plan details
    message_text = """<b>╔════❰ ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣</b>

<b>🔹 BRONZE PLAN:</b>
<b>   ┣⪼ Daily Limit:</b> <code>1,000 files</code>
<b>   ┣⪼ Duration:</b> <code>3 Days</code>
<b>   ┗⪼ Price:</b> <code>50 RS. </code>

<b>🔹 SILVER PLAN:</b>
<b>   ┣⪼ Daily Limit:</b> <code>1,500 files</code>
<b>   ┣⪼ Duration:</b> <code>7 days</code>
<b>   ┗⪼ Price:</b> <code>90 RS </code>

<b>🔹 GOLD PLAN:</b>
<b>   ┣⪼ Daily Limit:</b> <code>3,000 files</code>
<b>   ┣⪼ Duration:</b> <code>15 days</code>
<b>   ┗⪼ Price:</b> <code>130 RS.</code>

<b>🔹 DIAMOND PLAN:</b>
<b>   ┣⪼ Daily Limit:</b> <code>7,777 files</code>
<b>   ┣⪼ Duration:</b> <code>30 days</code>
<b>   ┗⪼ Price:</b> <code>200 RS.</code>

<b>║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪</b>

<b>🔸 Use /myplan to check your current plan status
🔸 Contact admin to upgrade your plan</b>"""

    # Add button to contact admin
    buttons = [[
        InlineKeyboardButton('💎 Contact Admin', url=f'https://t.me/itz_thanos')
    ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        message_text,
        reply_markup=reply_markup,
        quote=True
    )

# Command to list all users (admin only)
@Client.on_message(filters.command("users") & filters.private & filters.user(Config.BOT_OWNER))
async def users_command(client, message):
    try:
        all_users = await db.get_all_users()
        
        if not all_users:
            return await message.reply_text("No users found in database or database connection issue.")
        
        # Create a paginated system if there are many users
        users_text = "<b>All Users:</b>\n\n"
        user_count = 0
        
        try:
            # Initialize empty list in case async iteration fails
            users_list = []
            
            # Try to get all users into a list first
            try:
                async for user in all_users:
                    users_list.append(user)
            except Exception as e:
                print(f"Error iterating users: {e}")
                # Return early with a message about database issues
                return await message.reply_text(f"<b>Error retrieving users from database:</b> Database connection issue. Please try again later.")
            
            # If we have no users (unlikely given the earlier check, but just in case)
            if not users_list:
                return await message.reply_text("No users found in database.")
            
            # Process each user
            for user in users_list:
                user_id = user.get("id", "Unknown ID")
                user_name = user.get("name", "Unknown")
                
                try:
                    user_plan = await db.get_user_plan(user_id)
                except Exception as e:
                    print(f"Error getting plan for user {user_id}: {e}")
                    user_plan = None
                
                if not user_plan:
                    plan_info = "Free Plan"
                else:
                    plan_info = user_plan.get("plan_name", "Unknown Plan")
                    
                    # Add time remaining if not free plan
                    if user_plan.get("plan_type") != "free":
                        try:
                            current_time = time.time()
                            end_time = user_plan.get("end_time", 0)
                            if end_time > current_time:
                                remaining = format_time_remaining(end_time - current_time)
                                plan_info += f" ({remaining} left)"
                            else:
                                plan_info += " (Expired)"
                        except Exception as e:
                            print(f"Error calculating time remaining: {e}")
                            plan_info += " (Error calculating time)"
                
                users_text += f"<b>ID:</b> <code>{user_id}</code>\n<b>Name:</b> {user_name}\n<b>Plan:</b> {plan_info}\n\n"
                user_count += 1
                
                # Split messages if too long
                if user_count >= 20:  # Show 20 users per message
                    await message.reply_text(users_text)
                    users_text = "<b>All Users (continued):</b>\n\n"
                    user_count = 0
            
            if user_count > 0:
                await message.reply_text(users_text)
                
        except Exception as e:
            print(f"Error processing users list: {e}")
            await message.reply_text(f"<b>Error processing users list:</b> {str(e)}")
            
    except Exception as e:
        print(f"Error in users_command: {e}")
        await message.reply_text(f"<b>Error retrieving users:</b> Database connection issue. Please try again later.")

# Command to add plan to a user (admin only)
@Client.on_message(filters.command("adduser") & filters.private & filters.user(Config.BOT_OWNER))
async def add_user_command(client, message):
    # Check command format
    command_parts = message.text.split(" ", 1)
    if len(command_parts) != 2:
        return await message.reply_text(
            "<b>❌ Wrong format!</b>\n\n"
            "<b>Correct usage:</b> <code>/adduser user_id</code>\n"
            "<i>Example:</i> <code>/adduser 123456789</code>"
        )
    
    # Get user ID from command
    try:
        target_user_id = int(command_parts[1].strip())
    except ValueError:
        return await message.reply_text("<b>❌ Invalid user ID! It must be a number.</b>")
    
    # Check if user exists
    user_exists = await db.is_user_exist(target_user_id)
    if not user_exists:
        return await message.reply_text(f"<b>❌ User with ID {target_user_id} not found in the database.</b>")
    
    # Create plan selection buttons in two rows
    buttons = []
    plan_buttons = []
    
    # Organize plans into pairs for two rows
    for i, (plan_type, plan_details) in enumerate(PLANS.items()):
        if plan_type != "free":  # Skip free plan from buttons
            plan_button = InlineKeyboardButton(
                f"{plan_details['name']} - {plan_details['files_limit']} files",
                callback_data=f"assign_plan:{target_user_id}:{plan_type}"
            )
            
            # Add to temporary list
            plan_buttons.append(plan_button)
            
            # When we have 2 buttons or it's the last item, add to buttons
            if len(plan_buttons) == 2 or i == len(PLANS) - 1:
                buttons.append(plan_buttons.copy())
                plan_buttons = []
    
    # Add Ban User button
    buttons.append([InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user:{target_user_id}")])
    
    # Add Cancel button
    buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel_add_plan")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        f"<b>Select a plan to assign to user with ID:</b> <code>{target_user_id}</code>",
        reply_markup=reply_markup
    )

# Callback for plan selection
@Client.on_callback_query(filters.regex(r'^assign_plan:(\d+):(\w+)'))
async def assign_plan_callback(client, callback_query):
    # Only allow bot owner to assign plans
    if callback_query.from_user.id != Config.BOT_OWNER:
        return await callback_query.answer("You are not authorized to assign plans.", show_alert=True)
    
    # Parse callback data
    parts = callback_query.data.split(":")
    target_user_id = int(parts[1])
    plan_type = parts[2]
    
    # Get plan details
    plan_details = PLANS.get(plan_type)
    if not plan_details:
        return await callback_query.answer("Invalid plan selected.", show_alert=True)
    
    # Create plan data
    current_time = time.time()
    end_time = current_time + (plan_details["duration"] * 3600) if plan_details["duration"] > 0 else 0
    
    user_plan = {
        "plan_type": plan_type,
        "plan_name": plan_details["name"],
        "start_time": current_time,
        "end_time": end_time,
        "daily_limit": plan_details["daily_limit"],
        "files_limit": plan_details["files_limit"],
        "files_forwarded_today": 0,
        "last_day": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    # Update user plan in database
    await db.update_user_plan(target_user_id, user_plan)
    
    # Notify admin
    await callback_query.message.edit_text(
        f"<b>✅ Successfully assigned {plan_details['name']} to user with ID:</b> <code>{target_user_id}</code>"
    )
    
    # Try to notify the target user
    try:
        if plan_details["duration"] > 0:
            duration_text = f"{plan_details['duration']} hours" if plan_details["duration"] < 24 else f"{plan_details['duration'] // 24} days"
            await client.send_message(
                chat_id=target_user_id,
                text=f"<b>🎉 Congratulations!</b>\n\n"
                     f"<b>You have been upgraded to {plan_details['name']}!</b>\n\n"
                     f"<b>Plan Details:</b>\n"
                     f"• <b>Duration:</b> {duration_text}\n"
                     f"• <b>Daily Limit:</b> {plan_details['daily_limit']} files\n"
                     f"• <b>Total Files:</b> {plan_details['files_limit']} files\n\n"
                     f"<b>Use /myplan to check your current plan details and limits.</b>"
            )
    except Exception as e:
        await callback_query.message.reply_text(
            f"<b>⚠️ Couldn't notify user:</b> {str(e)}"
        )

# Callback for send plans command button
@Client.on_callback_query(filters.regex(r'^send_plans_command'))
async def send_plans_command_callback(client, callback_query):
    # Execute the /plans command directly when this button is clicked
    try:
        # Create a message object programmatically with the /plans command
        await plans_command(client, callback_query.message)
        # Answer the callback to remove loading state
        await callback_query.answer("Plans information loaded!")
    except Exception as e:
        print(f"Error in send_plans_command: {e}")
        await callback_query.answer("Error loading plans. Please use /plans command directly.", show_alert=True)

# Callback for upgrade plan button (keeping for backward compatibility)
@Client.on_callback_query(filters.regex(r'^upgrade_plan'))
async def upgrade_plan_callback(client, callback_query):
    await callback_query.answer("Contact the bot owner to upgrade your plan.", show_alert=True)

# Callback for ban user
@Client.on_callback_query(filters.regex(r'^ban_user:(\d+)'))
async def ban_user_callback(client, callback_query):
    # Only allow bot owner to ban users
    if callback_query.from_user.id != Config.BOT_OWNER:
        return await callback_query.answer("You are not authorized to ban users.", show_alert=True)
    
    # Parse callback data
    parts = callback_query.data.split(":")
    target_user_id = int(parts[1])
    
    try:
        # Ban the user in the database
        await db.ban_user(target_user_id, ban_reason="Banned by admin")
        
        # Update the message to show success
        await callback_query.message.edit_text(
            f"<b>🚫 User with ID:</b> <code>{target_user_id}</code> <b>has been banned successfully.</b>"
        )
        
        # Try to notify the user
        try:
            await client.send_message(
                chat_id=target_user_id,
                text="<b>⚠️ Your account has been banned from using this bot.</b>\n\n"
                     "<b>If you believe this is an error, please contact the administrator.</b>"
            )
        except Exception as e:
            print(f"Error notifying banned user: {e}")
            
    except Exception as e:
        # Handle any errors
        print(f"Error banning user: {e}")
        await callback_query.message.edit_text(
            f"<b>❌ Error banning user:</b> {str(e)}"
        )

# Callback for cancel add plan
@Client.on_callback_query(filters.regex(r'^cancel_add_plan'))
async def cancel_add_plan_callback(client, callback_query):
    if callback_query.from_user.id != Config.BOT_OWNER:
        return await callback_query.answer("You are not authorized.", show_alert=True)
    
    await callback_query.message.edit_text("<b>❌ Plan assignment cancelled.</b>")

# Command to remove premium plan from a user (admin only)
@Client.on_message(filters.command("removeuser") & filters.private & filters.user(Config.BOT_OWNER))
async def remove_user_plan_command(client, message):
    # Check command format
    command_parts = message.text.split(" ", 1)
    if len(command_parts) != 2:
        return await message.reply_text(
            "<b>❌ Wrong format!</b>\n\n"
            "<b>Correct usage:</b> <code>/removeuser user_id</code>\n"
            "<i>Example:</i> <code>/removeuser 123456789</code>"
        )
    
    # Get user ID from command
    try:
        target_user_id = int(command_parts[1].strip())
    except ValueError:
        return await message.reply_text("<b>❌ Invalid user ID! It must be a number.</b>")
    
    # Check if user exists
    user_exists = await db.is_user_exist(target_user_id)
    if not user_exists:
        return await message.reply_text(f"<b>❌ User with ID {target_user_id} not found in the database.</b>")
    
    # Get user's current plan
    user_plan = await db.get_user_plan(target_user_id)
    if not user_plan:
        return await message.reply_text(f"<b>✓ User is already on Free Plan.</b>")
    
    if user_plan.get("plan_type") == "free":
        return await message.reply_text(f"<b>✓ User is already on Free Plan.</b>")
    
    # Confirm removing plan
    buttons = [
        [InlineKeyboardButton("✅ Yes, Remove Plan", callback_data=f"confirm_remove_plan:{target_user_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_remove_plan")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    current_plan = user_plan.get("plan_name", "Unknown")
    
    await message.reply_text(
        f"<b>⚠️ Are you sure you want to remove {current_plan} from user with ID:</b> <code>{target_user_id}</code>?\n\n"
        f"<b>This will downgrade the user to the Free Plan.</b>",
        reply_markup=reply_markup
    )

# Callback for confirming plan removal
@Client.on_callback_query(filters.regex(r'^confirm_remove_plan:(\d+)'))
async def confirm_remove_plan_callback(client, callback_query):
    # Only allow bot owner to remove plans
    if callback_query.from_user.id != Config.BOT_OWNER:
        return await callback_query.answer("You are not authorized to remove plans.", show_alert=True)
    
    # Parse callback data
    parts = callback_query.data.split(":")
    target_user_id = int(parts[1])
    
    # Get user's current plan for notification purposes
    user_plan = await db.get_user_plan(target_user_id)
    old_plan_name = user_plan.get("plan_name", "Premium Plan") if user_plan else "Premium Plan"
    
    # Create free plan data
    current_time = time.time()
    current_day = datetime.datetime.now().strftime("%Y-%m-%d")
    
    free_plan = {
        "plan_type": "free",
        "plan_name": PLANS["free"]["name"],
        "start_time": current_time,
        "end_time": 0,  # Never expires for free plan
        "daily_limit": PLANS["free"]["daily_limit"],
        "files_limit": PLANS["free"]["files_limit"],
        "files_forwarded_today": 0,
        "last_day": current_day
    }
    
    # Update user plan in database
    await db.update_user_plan(target_user_id, free_plan)
    
    # Notify admin
    await callback_query.message.edit_text(
        f"<b>✅ Successfully removed premium plan from user with ID:</b> <code>{target_user_id}</code>\n"
        f"<b>User has been downgraded to Free Plan.</b>"
    )
    
    # Log the plan change
    try:
        from plugins.logger import log_to_channel
        await log_to_channel(
            f"User <code>{target_user_id}</code> downgraded from <b>{old_plan_name}</b> to <b>Free Plan</b>."
        )
    except Exception as e:
        print(f"Error logging plan change: {e}")
    
    # Try to notify the target user
    try:
        await client.send_message(
            chat_id=target_user_id,
            text=f"<b>📢 Plan Update</b>\n\n"
                 f"<b>Your premium plan has been removed.</b>\n\n"
                 f"<b>You have been downgraded to Free Plan:</b>\n"
                 f"• <b>Daily Limit:</b> {PLANS['free']['daily_limit']} files\n\n"
                 f"<b>Use /myplan to check your current plan details.</b>"
        )
    except Exception as e:
        await callback_query.message.reply_text(
            f"<b>⚠️ Couldn't notify user:</b> {str(e)}"
        )

# Callback for canceling plan removal
@Client.on_callback_query(filters.regex(r'^cancel_remove_plan'))
async def cancel_remove_plan_callback(client, callback_query):
    if callback_query.from_user.id != Config.BOT_OWNER:
        return await callback_query.answer("You are not authorized.", show_alert=True)
    
    await callback_query.message.edit_text("<b>❌ Plan removal cancelled.</b>")

# Check if user has hit their daily limit
async def check_user_limit(user_id):
    try:
        # Create a simple cache to reduce database load
        cache_key = f"user_plan_{user_id}"
        
        # Special fast path for bot owner
        if user_id == Config.BOT_OWNER:
            print(f"Bot owner detected! Providing unlimited access to user ID: {user_id}")
            # Create a special infinity plan for bot owner
            infinity_plan = {
                "plan_type": "infinity",
                "plan_name": "Infinity Plan (Owner)",
                "start_time": time.time(),
                "end_time": 0,  # Never expires
                "daily_limit": float('inf'),  # Infinite daily limit
                "files_limit": float('inf'),  # Infinite total limit
                "files_forwarded_today": 0,
                "last_day": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Try to update in database but don't fail if database is down
            try:
                await db.update_user_plan(user_id, infinity_plan)
            except Exception as e:
                print(f"Database error updating bot owner plan, but proceeding with unlimited access: {e}")
            
            # Always return True for bot owner regardless of database state
            return True, infinity_plan
        
        # For normal users, check if we have a cached plan first
        if hasattr(db, 'cache') and cache_key in db.cache.get('plans', {}):
            cached_plan = db.cache['plans'][cache_key]
            
            # Check if cache is still valid (less than 5 minutes old)
            cache_time = cached_plan.get('cache_time', 0)
            current_time = time.time()
            if current_time - cache_time < 300:  # 5 minutes
                # Use cached plan to avoid database query
                user_plan = cached_plan['plan']
                
                # Check daily limit for cached plan
                if user_plan.get("files_forwarded_today", 0) >= user_plan["daily_limit"]:
                    return False, user_plan
                    
                return True, user_plan
        
        # No valid cache, proceed with database query
        try:
            user_plan = await db.get_user_plan(user_id)
        except Exception as e:
            print(f"Error retrieving user plan, providing free plan as fallback: {e}")
            # If database error, create a free plan as fallback
            user_plan = None
        
        # If no plan exists, assign free plan
        if not user_plan:
            user_plan = {
                "plan_type": "free",
                "plan_name": PLANS["free"]["name"],
                "start_time": time.time(),
                "end_time": 0,
                "daily_limit": PLANS["free"]["daily_limit"],
                "files_limit": PLANS["free"]["files_limit"],
                "files_forwarded_today": 0,
                "last_day": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            try:
                await db.update_user_plan(user_id, user_plan)
            except Exception as e:
                print(f"Database error updating user plan, but proceeding with free plan: {e}")
    
        # Check if plan has expired (except free plan)
        current_time = time.time()
        if user_plan["plan_type"] != "free" and user_plan["end_time"] > 0 and user_plan["end_time"] < current_time:
            # Plan expired, assign free plan
            user_plan = {
                "plan_type": "free",
                "plan_name": PLANS["free"]["name"],
                "start_time": time.time(),
                "end_time": 0,
                "daily_limit": PLANS["free"]["daily_limit"],
                "files_limit": PLANS["free"]["files_limit"],
                "files_forwarded_today": 0,
                "last_day": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            try:
                await db.update_user_plan(user_id, user_plan)
            except Exception as e:
                print(f"Database error updating expired plan, continuing with free plan: {e}")
        
        # Reset daily counter if it's a new day
        current_day = datetime.datetime.now().strftime("%Y-%m-%d")
        if user_plan.get("last_day") != current_day:
            user_plan["files_forwarded_today"] = 0
            user_plan["last_day"] = current_day
            try:
                await db.update_user_plan(user_id, user_plan)
            except Exception as e:
                print(f"Database error updating daily counter, but proceeding: {e}")
        
        # Cache the plan for future use
        if hasattr(db, 'cache'):
            if 'plans' not in db.cache:
                db.cache['plans'] = {}
            db.cache['plans'][cache_key] = {
                'plan': user_plan,
                'cache_time': time.time()
            }
        
        # Check daily limit
        if user_plan.get("files_forwarded_today", 0) >= user_plan["daily_limit"]:
            return False, user_plan
        
        return True, user_plan
    except Exception as e:
        print(f"Unexpected error in check_user_limit, defaulting to allow access: {e}")
        
        # In case of error, if it's the bot owner, always allow
        if user_id == Config.BOT_OWNER:
            print("Error occurred but user is bot owner, providing unlimited access")
            infinity_plan = {
                "plan_type": "infinity",
                "plan_name": "Infinity Plan (Owner)",
                "daily_limit": float('inf'),
                "files_limit": float('inf'),
                "files_forwarded_today": 0
            }
            return True, infinity_plan
            
        # For other users, allow with a basic free plan
        free_plan = {
            "plan_type": "free",
            "plan_name": "Free Plan (Fallback)",
            "daily_limit": PLANS["free"]["daily_limit"],
            "files_limit": PLANS["free"]["files_limit"],
            "files_forwarded_today": 0
        }
        return True, free_plan

# Update user forwarded files count
async def update_user_forwarded_count(user_id, count=1):
    try:
        # Skip updating count for bot owner (infinity plan)
        if user_id == Config.BOT_OWNER:
            print(f"Skipping count update for bot owner with ID: {user_id}")
            return
            
        # Create a cache key for this user
        cache_key = f"user_plan_{user_id}"
        
        # Try to get the plan from cache first to avoid database query
        cached_plan = None
        if hasattr(db, 'cache') and 'plans' in db.cache and cache_key in db.cache['plans']:
            cached_data = db.cache['plans'][cache_key]
            cached_plan = cached_data['plan']
            # Update the cached plan directly
            current_day = datetime.datetime.now().strftime("%Y-%m-%d")
            if cached_plan.get("last_day") != current_day:
                cached_plan["files_forwarded_today"] = count
                cached_plan["last_day"] = current_day
            else:
                cached_plan["files_forwarded_today"] = cached_plan.get("files_forwarded_today", 0) + count
                
            # Update the cache with the new data
            if hasattr(db, 'cache') and 'plans' in db.cache:
                db.cache['plans'][cache_key]['plan'] = cached_plan
                
            # Try to update database in background but don't block other operations
            try:
                await db.update_user_plan(user_id, cached_plan)
            except Exception as e:
                print(f"Background database update failed for user {user_id}, but cache updated: {e}")
            return
        
        # If not in cache or cache isn't available, go to database
        try:
            user_plan = await db.get_user_plan(user_id)
        except Exception as e:
            print(f"Error getting user plan for ID {user_id} in update_user_forwarded_count: {e}")
            return
        
        if not user_plan:
            # If no plan exists, this shouldn't happen but just in case
            print(f"No plan exists for user ID {user_id} in update_user_forwarded_count")
            return
        
        current_day = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Reset counter if it's a new day
        if user_plan.get("last_day") != current_day:
            user_plan["files_forwarded_today"] = count
            user_plan["last_day"] = current_day
        else:
            user_plan["files_forwarded_today"] = user_plan.get("files_forwarded_today", 0) + count
        
        # Update cache for future access
        if hasattr(db, 'cache'):
            if 'plans' not in db.cache:
                db.cache['plans'] = {}
            db.cache['plans'][cache_key] = {
                'plan': user_plan,
                'cache_time': time.time()
            }
        
        try:
            await db.update_user_plan(user_id, user_plan)
            print(f"Successfully updated forward count for user {user_id} to {user_plan.get('files_forwarded_today')}")
        except Exception as e:
            print(f"Error updating forward count in database for user {user_id}: {e}")
            print("However, the count is still updated in memory for this session.")
    except Exception as e:
        print(f"Unexpected error in update_user_forwarded_count for user {user_id}: {e}")
        # Continue execution despite error