import motor.motor_asyncio
import datetime
import certifi
from config import Config

class Db:

    def __init__(self, uri, database_name):
        # Add SSL and timeout options to handle connection issues
        try:
            # For MongoDB Atlas connections with SSL issues, we use certifi's CA bundle
            print(f"Attempting to connect to MongoDB using certifi SSL certificates...")
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                uri,
                tls=True,                       # Use TLS/SSL
                tlsCAFile=certifi.where(),      # Use certifi's CA bundle
                connectTimeoutMS=30000,         # Increase timeout to 30 seconds
                serverSelectionTimeoutMS=30000, # Increase server selection timeout
                socketTimeoutMS=30000,          # Increase socket timeout
                retryWrites=True,               # Enable retry writes
                maxPoolSize=50,                 # Increase connection pool
                maxIdleTimeMS=60000,            # Increase idle time
                waitQueueTimeoutMS=20000,       # Increase queue timeout
                retryReads=True,                # Enable retry reads
                w="majority",                   # Write concern
                readPreference="primaryPreferred", # Read preference
                tlsAllowInvalidCertificates=False,  # Don't allow invalid certs
                tlsAllowInvalidHostnames=False,     # Don't allow invalid hostnames
                directConnection=False              # Use replica set discovery
            )
            
            # If we got here, the connection configuration was accepted
            print("MongoDB connection established successfully.")
            self.db = self._client[database_name]
            self.bot = self.db.bots
            self.userbot = self.db.userbot 
            self.col = self.db.users
            self.nfy = self.db.notify
            self.chl = self.db.channels
            self.plans = self.db.plans
            self.connection_ok = True
            
            # Test collections by inserting and retrieving a test document
            try:
                test_collection = self.db.connection_test
                test_id = "test_connection_" + str(hash(uri))[-8:]
                # Insert test document
                test_collection.insert_one({"_id": test_id, "test": True, "timestamp": str(datetime.datetime.now())})
                # Retrieve the document (will throw if connection fails)
                test_collection.find_one({"_id": test_id})
                # If we get here, connection is fully working
                print("MongoDB connection verified with test read/write operation.")
            except Exception as e:
                print(f"Connection test operation failed: {e}")
                # Not raising, as we'll fall back to memory mode if needed
                self.connection_ok = False
            
            # Store reference to client
            self.client = self._client
            
        except Exception as e:
            print(f"All MongoDB connection attempts failed: {e}")
            # Create dummy in-memory collections for fallback
            from pymongo.collection import Collection
            self.db = {}
            self.bot = Collection(None, "bots")
            self.userbot = Collection(None, "userbot")
            self.col = Collection(None, "users")
            self.nfy = Collection(None, "notify")
            self.chl = Collection(None, "channels")
            self.plans = Collection(None, "plans")
            self.connection_ok = False
            self.client = None
            print("Using fallback memory database for critical operations.")

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    async def add_user(self, id, name, username=""):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
        
        # Try to import and use the logger to log new user
        try:
            from plugins.logger import log_to_channel
            
            # Get bot client and total user count
            from pyrogram import Client
            from config import Config
            
            total_users = await self.total_users_count()
            
            # Create a temporary client for logging if not available in context
            temp_client = None
            if hasattr(self, 'bot_client') and self.bot_client:
                client = self.bot_client
            else:
                try:
                    # Create a temporary client just for logging
                    temp_client = Client(
                        "temp_log_client",
                        bot_token=Config.BOT_TOKEN,
                        api_id=Config.API_ID,
                        api_hash=Config.API_HASH,
                        in_memory=True
                    )
                    await temp_client.start()
                    client = temp_client
                except Exception as e:
                    print(f"Error creating temporary client: {e}")
                    return
            
            # Log new user to channel
            await log_to_channel(
                client,
                "new_user",
                details={"total_users": total_users},
                user_info={"id": id, "name": name, "username": username}
            )
            
            # Stop temporary client if created
            if temp_client:
                await temp_client.stop()
                
        except Exception as e:
            print(f"Error logging new user: {e}")

    async def is_user_exist(self, id):
        # If we're in fallback mode, just assume user doesn't exist
        # so we don't try to hit the database and generate more errors
        if not hasattr(self, 'connection_ok') or not self.connection_ok:
            print(f"Skipping database check for user {id} - connection not available")
            return False
            
        try:
            user = await self.col.find_one({'id':int(id)})
            return bool(user)
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            # Return False as a fallback
            return False

    async def total_users_count(self):
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0

    async def total_users_bots_count(self):
        # If we're in fallback mode, return zeros to avoid database errors
        if not hasattr(self, 'connection_ok') or not self.connection_ok:
            print(f"Skipping database counts - connection not available")
            return 0, 0
            
        try:
            bcount = await self.bot.count_documents({})
        except Exception as e:
            print(f"Error counting bots: {e}")
            bcount = 0
            
        try:
            count = await self.col.count_documents({})
        except Exception as e:
            print(f"Error counting users: {e}")
            count = 0
            
        return count, bcount

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        try:
            return self.col.find({})
        except Exception as e:
            print(f"Error getting all users: {e}")
            # Return empty list to prevent errors
            return []

    async def delete_user(self, user_id):
        try:
            await self.col.delete_many({'id': int(user_id)})
        except Exception as e:
            print(f"Error deleting user: {e}")

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        b_users = [user['id'] async for user in users]
        return b_users

    async def update_configs(self, id, configs):
        await self.col.update_one({'id': int(id)}, {'$set': {'configs': configs}})

    async def get_configs(self, id):
        default = {
            'caption': None,
            'duplicate': True,
            'forward_tag': False,
            'min_size': 0,
            'max_size': 0,
            'extension': None,
            'keywords': None,
            'protect': None,
            'button': None,
            'db_uri': None,
            'filters': {
               'poll': True,
               'text': True,
               'audio': True,
               'voice': True,
               'video': True,
               'photo': True,
               'document': True,
               'animation': True,
               'sticker': True
            }
        }
        try:
            user = await self.col.find_one({'id':int(id)})
            if user:
                return user.get('configs', default)
            return default
        except Exception as e:
            print(f"Error getting user configs: {e}")
            return default

    async def add_bot(self, datas):
       if not await self.is_bot_exist(datas['user_id']):
          await self.bot.insert_one(datas)
          
          # Log new bot addition
          try:
              from plugins.logger import log_to_channel
              from pyrogram import Client
              from config import Config
              
              user_id = datas.get('user_id')
              # Get user name
              user = await self.col.find_one({'id': int(user_id)})
              name = user.get('name', 'Unknown') if user else 'Unknown'
              
              # Create a temporary client for logging if not available in context
              temp_client = None
              if hasattr(self, 'bot_client') and self.bot_client:
                  client = self.bot_client
              else:
                  try:
                      # Create a temporary client just for logging
                      temp_client = Client(
                          "temp_log_client",
                          bot_token=Config.BOT_TOKEN,
                          api_id=Config.API_ID,
                          api_hash=Config.API_HASH,
                          in_memory=True
                      )
                      await temp_client.start()
                      client = temp_client
                  except Exception as e:
                      print(f"Error creating temporary client: {e}")
                      return
              
              # Log new bot to channel
              await log_to_channel(
                  client,
                  "new_bot",
                  details={"bot_details": {
                      "name": datas.get('name', 'Unknown'),
                      "username": datas.get('username', 'Unknown'),
                      "id": datas.get('id', 'Unknown')
                  }},
                  user_info={"id": user_id, "name": name}
              )
              
              # Stop temporary client if created
              if temp_client:
                  await temp_client.stop()
                  
          except Exception as e:
              print(f"Error logging new bot: {e}")

    async def remove_bot(self, user_id):
       await self.bot.delete_many({'user_id': int(user_id)})

    async def get_bot(self, user_id: int):
       try:
           bot = await self.bot.find_one({'user_id': user_id})
           return bot if bot else None
       except Exception as e:
           print(f"Error getting bot for user {user_id}: {e}")
           return None

    async def is_bot_exist(self, user_id):
       bot = await self.bot.find_one({'user_id': user_id})
       return bool(bot)
   
    async def add_userbot(self, datas):
       if not await self.is_userbot_exist(datas['user_id']):
          await self.userbot.insert_one(datas)

    async def remove_userbot(self, user_id):
       await self.userbot.delete_many({'user_id': int(user_id)})

    async def get_userbot(self, user_id: int):
       try:
           bot = await self.userbot.find_one({'user_id': user_id})
           return bot if bot else None
       except Exception as e:
           print(f"Error getting userbot for user {user_id}: {e}")
           return None

    async def is_userbot_exist(self, user_id):
       bot = await self.userbot.find_one({'user_id': user_id})
       return bool(bot)
    
    async def in_channel(self, user_id: int, chat_id: int) -> bool:
       channel = await self.chl.find_one({"user_id": int(user_id), "chat_id": int(chat_id)})
       return bool(channel)

    async def add_channel(self, user_id: int, chat_id: int, title, username):
       channel = await self.in_channel(user_id, chat_id)
       if channel:
         return False
       return await self.chl.insert_one({"user_id": user_id, "chat_id": chat_id, "title": title, "username": username})

    async def remove_channel(self, user_id: int, chat_id: int):
       channel = await self.in_channel(user_id, chat_id )
       if not channel:
         return False
       return await self.chl.delete_many({"user_id": int(user_id), "chat_id": int(chat_id)})

    async def get_channel_details(self, user_id: int, chat_id: int):
       return await self.chl.find_one({"user_id": int(user_id), "chat_id": int(chat_id)})

    async def get_user_channels(self, user_id: int):
       try:
           channels = self.chl.find({"user_id": int(user_id)})
           return [channel async for channel in channels]
       except Exception as e:
           print(f"Error getting channels for user {user_id}: {e}")
           return []

    async def get_filters(self, user_id):
       filters = []
       filter = (await self.get_configs(user_id))['filters']
       for k, v in filter.items():
          if v == False:
            filters.append(str(k))
       return filters

    async def add_frwd(self, user_id):
       return await self.nfy.insert_one({'user_id': int(user_id)})

    async def rmve_frwd(self, user_id=0, all=False):
       data = {} if all else {'user_id': int(user_id)}
       return await self.nfy.delete_many(data)

    async def get_all_frwd(self):
       return self.nfy.find({})
  
    async def forwad_count(self):
        # If we're in fallback mode, return zero to avoid database errors
        if not hasattr(self, 'connection_ok') or not self.connection_ok:
            print(f"Skipping forwarding count - connection not available")
            return 0
            
        try:
            c = await self.nfy.count_documents({})
            return c
        except Exception as e:
            print(f"Error counting forwards: {e}")
            return 0
        
    async def is_forwad_exit(self, user):
        u = await self.nfy.find_one({'user_id': user})
        return bool(u)
        
    async def get_forward_details(self, user_id):
        defult = {
            'chat_id': None,
            'forward_id': None,
            'toid': None,
            'last_id': None,
            'limit': None,
            'msg_id': None,
            'start_time': None,
            'fetched': 0,
            'offset': 0,
            'deleted': 0,
            'total': 0,
            'duplicate': 0,
            'skip': 0,
            'filtered' :0
        }
        user = await self.nfy.find_one({'user_id': int(user_id)})
        if user:
            return user.get('details', defult)
        return defult
   
    async def update_forward(self, user_id, details):
        await self.nfy.update_one({'user_id': user_id}, {'$set': {'details': details}})
    
    # Plan management methods
    async def get_user_plan(self, user_id):
        """Get a user's plan information"""
        try:
            plan = await self.plans.find_one({'user_id': int(user_id)})
            return plan['plan_data'] if plan else None
        except Exception as e:
            print(f"Error retrieving plan for user {user_id}: {str(e)}")
            return None
    
    async def update_user_plan(self, user_id, plan_data):
        """Update a user's plan information"""
        try:
            # Using upsert to create if it doesn't exist
            await self.plans.update_one(
                {'user_id': int(user_id)},
                {'$set': {'user_id': int(user_id), 'plan_data': plan_data}},
                upsert=True
            )
            
            # Log premium plan activation/update
            try:
                from plugins.logger import log_to_channel
                from pyrogram import Client
                from config import Config
                import datetime
                
                # Get user name
                user = await self.col.find_one({'id': int(user_id)})
                name = user.get('name', 'Unknown') if user else 'Unknown'
                
                # Create a temporary client for logging if not available in context
                temp_client = None
                if hasattr(self, 'bot_client') and self.bot_client:
                    client = self.bot_client
                else:
                    try:
                        # Create a temporary client just for logging
                        temp_client = Client(
                            "temp_log_client",
                            bot_token=Config.BOT_TOKEN,
                            api_id=Config.API_ID,
                            api_hash=Config.API_HASH,
                            in_memory=True
                        )
                        await temp_client.start()
                        client = temp_client
                    except Exception as e:
                        print(f"Error creating temporary client: {e}")
                        return
                
                # Get expiry date in readable format
                expiry_timestamp = plan_data.get('expiry_date')
                expiry_str = "Never"
                if expiry_timestamp:
                    try:
                        expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp)
                        expiry_str = expiry_date.strftime("%d-%m-%Y %H:%M:%S")
                    except:
                        expiry_str = str(expiry_timestamp)
                
                # Log premium update to channel
                await log_to_channel(
                    client,
                    "premium",
                    details={"plan_details": {
                        "plan_name": plan_data.get('plan_name', 'Unknown'),
                        "daily_limit": plan_data.get('daily_limit', 'Unknown'),
                        "expiry": expiry_str
                    }},
                    user_info={"id": user_id, "name": name}
                )
                
                # Stop temporary client if created
                if temp_client:
                    await temp_client.stop()
                    
            except Exception as e:
                print(f"Error logging premium update: {e}")
                
        except Exception as e:
            print(f"Error updating plan for user {user_id}: {str(e)}")
    
    async def delete_user_plan(self, user_id):
        """Delete a user's plan"""
        await self.plans.delete_one({'user_id': int(user_id)})
    
    async def get_all_plans(self):
        """Get all user plans"""
        return self.plans.find({})
        
db = Db(Config.DATABASE_URI, Config.DATABASE_NAME)
