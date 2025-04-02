# VJ Forward Bot

<b>Auto Restart All User Forwarding After Bot Restarted.</b>

![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=Welcome+To+VJ+Forward+Bot+!)

## Deployment Options

### 1. GitHub to Koyeb Deployment

#### Fork and Configure on GitHub
1. Fork this repository to your GitHub account
2. Create `.env` file with your variables (see variables section below)
3. Make sure to remove any hardcoded credentials from the code

#### Deploy on Koyeb
1. Visit [Koyeb](https://koyeb.com) and sign up/log in
2. Create a new application and select "GitHub" as the deployment method
3. Connect your GitHub account and select the forked repository
4. Configure the following settings:
   - Select "Dockerfile" as the build method
   - Set environment variables according to the variables section below
   - Configure health check path as `/ping`
5. Deploy the application

### 2. Local Deployment
1. Clone the repository: `git clone [your-fork-url]`
2. Create a `.env` file with all required variables
3. Install requirements: `pip install -r requirements.txt`
4. Run the bot: `python main.py`

### 3. Docker Deployment
```bash
# Pull the image
docker pull your-username/vj-forward-bot:latest

# Run the container
docker run -d --name forward-bot \
  --restart always \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e BOT_OWNER=your_user_id \
  -e DATABASE_URI=your_mongodb_uri \
  your-username/vj-forward-bot:latest
```

## UptimeRobot Setup (For Free Hosting)
To keep the bot running 24/7 on free hosting platforms, use UptimeRobot:

1. Go to https://uptimerobot.com/ and create a free account
2. After logging in, click "Add New Monitor"
3. Select "HTTP(s)" as the monitor type
4. Enter a name like "Telegram Forward Bot"
5. For the URL, enter your app URL with /ping endpoint
6. Set monitoring interval to 5 minutes
7. Save the monitor

## Features

- [x] Public Forward (Bot)
- [x] Private Forward (User Bot)
- [x] Custom Caption 
- [x] Custom Button
- [x] Skip Duplicate Messages
- [x] Skip Messages Based On Extensions & Keywords & Size
- [x] Filter Type Of Messages
- [x] Auto Restart Pending Task After Bot Restart 
- [x] Adjustable Forward Speed Settings for Bot and Userbot
  - Speed range: 20-50 messages per minute
  - Separate controls for bot and userbot forwarding
  - Adjustable in +/- 5 message increments
- [x] Premium Plans with Daily Message Limits


<b>To Know About All Features, Join My <a href='https://t.me/VJ_Botz'>Update Channel</a>.</b>

## Commands

```
start - check I'm alive 
forward - forward messages
unequify - delete duplicate media messages in chats
settings - configure your settings
stop - stop your ongoing tasks
reset - reset your settings
myplan - check your current plan status
plans - view all available premium plans
speed - adjust bot forwarding speed (admin only)
restart - restart server (owner only)
resetall - reset all users settings (owner only)
broadcast - broadcast a message to all your users (owner only)
```

## Environment Variables

### Required Variables
* `API_ID` - API ID from [my.telegram.org](https://my.telegram.org)
* `API_HASH` - API Hash from [my.telegram.org](https://my.telegram.org)
* `BOT_TOKEN` - Bot token from [@BotFather](https://t.me/BotFather)
* `BOT_OWNER` - Telegram Account ID of the bot owner
* `DATABASE_URI` - MongoDB connection URI from [MongoDB Atlas](https://mongodb.com) - [Video Tutorial](https://youtu.be/DAHRmFdw99o)

### Optional Variables
* `BOT_SESSION` - Custom session name for the bot (default: "bot_session")
* `DATABASE_NAME` - Name of the MongoDB database (default: "Forward-Bot")
* `LOG_CHANNEL` - Channel ID for logging activities (must start with -100)
* `FORCE_CHANNEL_ID` - Channel ID for forced subscription (must start with -100)
* `FORCE_CHANNEL_USERNAME` - Channel username for forced subscription (without @)

## Credits

* <b>[Tech MK](https://t.me/itz_THANOS)</b>
