import os
from config import Config

class  Script(object):
  START_TXT = """<b><blockquote>ʜɪ "<a href="tg://settings">{}</a>"</blockquote>
  
ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇᴅ ꜰᴏʀᴡᴀʀᴅ ʙᴏᴛ
ɪ ᴄᴀɴ ꜰᴏʀᴡᴀʀᴅ ᴀʟʟ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴏɴᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀɴɴᴇʟ</b>

**ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍᴇ**"""
  
  FORCE_SUB_TXT = """<b><blockquote>ʜᴇʏ "<a href="tg://settings">{}</a>" 👋</blockquote>

ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ!

ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ "ᴛʀʏ ᴀɢᴀɪɴ" ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.</b>"""
  HELP_TXT = """<b><u>Bot Details</b></u>

<b><u>💢 Features:</b></u>
<b>► Forward message from public channel to your channel without admin permission. if the channel is private need admin permission, if you can't give admin permission then use userbot, but in userbot there is a chance to get your account ban so use fake account
► custom caption
► custom button
► skip duplicate messages
► filter type of messages
► premium plans with higher daily limits</b>
"""

  COMMANDS_TXT = """<b><u>📚 Available commands:</b></u>
<b>⏣ /start - check I'm alive 
⏣ /forward - forward messages
⏣ /settings - configure your settings
⏣ /unequify - delete duplicate media messages in chats
⏣ /stop - stop your ongoing tasks
⏣ /reset - reset your settings
⏣ /myplan - check your current plan status
⏣ /plans - view all available premium plans</b>
"""

  PLANS_INFO_TXT = """<b><u>💎 Available Plans</b></u>

<b>• __Free Plan:__</b>
   <b>- Daily Limit:</b> <code>100 files per day</code>
   <b>- Duration:</b> <code>Unlimited</code>
   <b>- Price:</b> <code>Free</code>

<b>• __Bronze Plan:__</b>
   <b>- Daily Limit:</b> <code>1,000 files</code>
   <b>- Duration:</b> <code>3 hours</code>
   <b>- Price:</b> <code>Contact Admin</code>

<b>• __Silver Plan:__</b>
   <b>- Daily Limit:</b> <code>1,500 files per day</code>
   <b>- Duration:</b> <code>7 days</code>
   <b>- Price:</b> <code>Contact Admin</code>

<b>• __Gold Plan:__</b>
   <b>- Daily Limit:</b> <code>3,000 files per day</code>
   <b>- Duration:</b> <code>15 days</code>
   <b>- Price:</b> <code>Contact Admin</code>

<b>• __Diamond Plan:__</b>
   <b>- Daily Limit:</b> <code>7,777 files per day</code>
   <b>- Duration:</b> <code>30 days</code>
   <b>- Price:</b> <code>Contact Admin</code>

<b>Check your current plan: /myplan
View available plans: /plans
💡 Contact admin to upgrade your plan for higher daily limits</b>
"""

  SPEED_TXT = """<b><u>⚡ Forward Speed Settings</b></u>

<b>Current Forward Speed Settings:</b>
<b>• Bot Forward Speed:</b> <code>{} second(s)</code> (~ {} msgs/min)
<b>• Userbot Forward Speed:</b> <code>{} second(s)</code> (~ {} msgs/min)

<b>Speed Limits:</b>
<i>• Minimum: 20 messages PM
• Maximum: 50 messages PM </i>

<b>⚠️ Warning:</b> <i>Using very high speeds may cause your account to be rate-limited by Telegram</i>
"""
  
  HOW_USE_TXT = """<b><u>⚠️ Before Forwarding:</b></u>
<b>► __add a bot or userbot__
► __add atleast one to channel__ `(your bot/userbot must be admin in there)`
► __You can add chats or bots by using /settings__
► __if the **From Channel** is private your userbot must be member in there or your bot must need admin permission in there also__
► __Then use /forward to forward messages__

► ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ [ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ](https://youtu.be/wO1FE-lf35I)</b>"""
  
  ABOUT_TXT = """<b>
╔════❰ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼📃ʙᴏᴛ : [Fᴏʀᴡᴀᴅ Bᴏᴛ](https://t.me/Forwarder4U_BOT)
║┣⪼👦Cʀᴇᴀᴛᴏʀ : [Tʜᴀɴᴏs 👑](https://t.me/itz_THANOS)
║┣⪼🤖Uᴘᴅᴀᴛᴇ : [Kᴏʀɴ Bᴏᴛs](https://t.me/iCrunchKornBots)
║┣⪼📡Hᴏsᴛᴇᴅ ᴏɴ : Sᴜᴘᴇʀ Fᴀsᴛ
║┣⪼🗣️Lᴀɴɢᴜᴀɢᴇ : Pʏᴛʜᴏɴ3
║┣⪼📚Lɪʙʀᴀʀʏ : Pʏʀᴏɢʀᴀᴍ Gᴀᴛʜᴇʀ 2.11.0 
║┣⪼🗒️Vᴇʀsɪᴏɴ : 0.18.3
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
</b>"""
  STATUS_TXT = """
╔════❰ ʙᴏᴛ sᴛᴀᴛᴜs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼**⏳ ʙᴏᴛ ᴜᴘᴛɪᴍᴇ:**`{}`
║┃
║┣⪼**👱 Tᴏᴛᴀʟ Usᴇʀs:** `{}`
║┃
║┣⪼**🤖 Tᴏᴛᴀʟ Bᴏᴛ:** `{}`
║┃
║┣⪼**🔃 Fᴏʀᴡᴀʀᴅɪɴɢs:** `{}`
║┃
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
"""
  FROM_MSG = "<b>❪ SET SOURCE CHAT ❫\n\nForward the last message or last message link of source chat. You'll be able to specify a range of message IDs to forward.\n/cancel - cancel this forwarding process</b>"
  START_MSG_ID = "<b>❪ SET START MESSAGE ID ❫\n\nEnter the start message ID for forwarding.\nThis is the first message that will be forwarded.\nDefault Start ID =</b> <code>1</code>\n/cancel <b>- cancel this forwarding process</b>"
  END_MSG_ID = "<b>❪ SET END MESSAGE ID ❫\n\nEnter the end message ID for forwarding.\nThis is the last message that will be forwarded.\nDefault End ID = </b><code>latest message</code>\n/cancel <b>- cancel this forwarding process</b>"
  TO_MSG = "<b>❪ CHOOSE TARGET CHAT ❫\n\nChoose your target chat from the given buttons.\n/cancel - Cancel this process</b>"
  SKIP_MSG = "<b>❪ SEND 0 TO CONTINUE ❫</b>\n<code>0</code>\n/cancel <b>- cancel this process</b>"
  CANCEL = "<b>Process Cancelled Succefully !</b>"
  BOT_DETAILS = "<b><u>📄 BOT DETAILS</b></u>\n\n<b>➣ NAME:</b> <code>{}</code>\n<b>➣ BOT ID:</b> <code>{}</code>\n<b>➣ USERNAME:</b> @{}"
  USER_DETAILS = "<b><u>📄 USERBOT DETAILS</b></u>\n\n<b>➣ NAME:</b> <code>{}</code>\n<b>➣ USER ID:</b> <code>{}</code>\n<b>➣ USERNAME:</b> @{}"  
         
  TEXT = """
╔════❰ ғᴏʀᴡᴀʀᴅ sᴛᴀᴛᴜs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼<b>📥 Sᴛᴀʀᴛ ɪᴅ :</b> <a href="https://t.me/c/{}/{}"><code>{}</code></a>
║┃
║┣⪼<b>📤 Lᴀsᴛ ɪᴅ :</b> <a href="https://t.me/c/{}/{}"><code>{}</code></a>
║┃
║┣⪼<b>🕵 ғᴇᴄʜᴇᴅ Msɢ :</b> <code>{}</code>
║┃
║┣⪼<b>✅ sᴜᴄᴄᴇғᴜʟʟʏ Fᴡᴅ :</b> <code>{}</code>
║┃
║┣⪼<b>👥 ᴅᴜᴘʟɪᴄᴀᴛᴇ Msɢ :</b> <code>{}</code>
║┃
║┣⪼<b>🗑 ᴅᴇʟᴇᴛᴇᴅ Msɢ :</b> <code>{}</code>
║┃
║┣⪼<b>🪆 Sᴋɪᴘᴘᴇᴅ Msɢ :</b> <code>{}</code>
║┃
║┣⪼<b>🔁 Fɪʟᴛᴇʀᴇᴅ Msɢ :</b> <code>{}</code>
║┃
║┣⪼<b>📊 Cᴜʀʀᴇɴᴛ Sᴛᴀᴛᴜs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 Pᴇʀᴄᴇɴᴛᴀɢᴇ:</b> <code>{}</code> %
║╰━━━━━━━━━━━━━━━➣ 
╚════❰ {} ❱══❍⊱❁۪۪
"""
  DUPLICATE_TEXT = """
╔════❰ ᴜɴᴇǫᴜɪғʏ sᴛᴀᴛᴜs ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ <b>ғᴇᴛᴄʜᴇᴅ ғɪʟᴇs:</b> <code>{}</code>
║┃
║┣⪼ <b>ᴅᴜᴘʟɪᴄᴀᴛᴇ ᴅᴇʟᴇᴛᴇᴅ:</b> <code>{}</code> 
║╰━━━━━━━━━━━━━━━➣
╚════❰ {} ❱══❍⊱❁۪۪
"""
  DOUBLE_CHECK = """<b><u>DOUBLE CHECKING ⚠️</b></u>
<code>Before forwarding the messages Click the Yes button only after checking the following</code>

<b>★ YOUR BOT:</b> [{botname}](t.me/{botuname})
<b>★ FROM CHANNEL:</b> `{from_chat}`
<b>★ TO CHANNEL:</b> `{to_chat}`
<b>★ SKIP MESSAGES:</b> `{skip}`
<b>★ START MESSAGE ID:</b> `{start_id}`
<b>★ END MESSAGE ID:</b> `{end_id}`

<i>° [{botname}](t.me/{botuname}) must be admin in **TARGET CHAT**</i> (`{to_chat}`)
<i>° If the **SOURCE CHAT** is private your userbot must be member or your bot must be admin in there also</b></i>

<b>If the above is checked then the yes button can be clicked</b>"""
  
SETTINGS_TXT = """<b>change your settings as your wish</b>"""

# Plan related messages
PLAN_LIMIT_REACHED = """<b>⚠️ DAILY LIMIT REACHED ❗️</b>

<b>You have reached your daily forwarding limit of <code>{}</code> files.</b>

<b>Upgrade to a premium plan to forward more files and enjoy higher daily limits:</b>
• <b>Bronze Plan:</b> 1,000 files for 3 days
• <b>Silver Plan:</b> 1,500 files/day for 7 days
• <b>Gold Plan:</b> 3,000 files/day for 15 days
• <b>Diamond Plan:</b> 7,777 files/day for 30 days

<b>Contact the bot owner to upgrade your plan.</b>"""

PLAN_EXPIRED = """<b>⚠️ YOUR PREMIUM PLAN HAS EXPIRED ❗️</b>

<b>Your {} has expired. You have been downgraded to the Free Plan with a daily limit of 100 files.</b>

<b>To enjoy premium features again, contact the bot owner to upgrade your plan.</b>"""
