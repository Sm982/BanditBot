import discord
import os
import asyncio
import importlib.util
import threading
from aiohttp import web
from logger import logger
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from database.db_manager import CountingDatabase
from database.ticket_db import ticketDatabase
from cogs.prototicket import TicketControlView


# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD'))
LOGS_CHANNEL_ID = int(os.getenv('DISCORD_GUILD_LOGS_CHANNEL'))
EVENTS_CHANNEL_ID = int(os.getenv('DISCORD_EVENTS_CHANNEL'))
GENERAL_CHANNEL_ID = int(os.getenv('DISCORD_GENERAL_CHANNEL'))
SUPERSECRET_CHANNEL_ID = int(os.getenv('DISCORD_SUPERS_CHANNEL'))
SECRET_CHANNEL_ID = int(os.getenv('DISCORD_SECRET_CHANNEL'))
COUNTING_CHANNEL_ID = int(os.getenv('DISCORD_COUNTING'))
CREATOR_USER_ID = int(os.getenv('DISCORD_CREATOR_USER_ID'))
STAFF_ROLE_ID= int(os.getenv('DISCORD_STAFF_ROLE'))

async def healthcheck(request):
    return web.json_response({"status": "ok"})

def start_health_server():
    loop = asyncio.new_event_loop()  # create a new event loop
    asyncio.set_event_loop(loop)
    app = web.Application()
    app.add_routes([web.get('/devbanditbot/health', healthcheck)])

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host="0.0.0.0", port=6363)
    loop.run_until_complete(site.start())
    print("Healthcheck server running on http://0.0.0.0:6363/health")
    loop.run_forever()

#disabling this as it's too annoying and doesn't work.
#threading.Thread(target=start_health_server, daemon=True).start()

class BanditBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents)
        self.counting_db = CountingDatabase()
        self.ticket_db = ticketDatabase()
        
        # Store important IDs
        self.creator_user_id = CREATOR_USER_ID
        self.guild_id = GUILD_ID
        self.logs_channel_id = LOGS_CHANNEL_ID
        self.events_channel_id = EVENTS_CHANNEL_ID
        self.general_channel_id = GENERAL_CHANNEL_ID #
        self.supersecret_general_channel_id = SUPERSECRET_CHANNEL_ID
        self.secret_general_channel_id = SECRET_CHANNEL_ID
        self.counting_channel_id = COUNTING_CHANNEL_ID
        self.staff_role_id = STAFF_ROLE_ID
        self.logs_channel = None
        self.events_channel = None
        self.banditColor = 0x0a8888
        
    async def setup_hook(self):
        # Load all cogs
        logger.info("Loading cogs...")
        cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
        await self.counting_db.initialize()
        await self.ticket_db.initialize()
        
        if not os.path.exists(cogs_dir):
            logger.error(f"Cogs directory not found at {cogs_dir}")
            os.makedirs(cogs_dir, exist_ok=True)
            logger.info(f"Created cogs directory at {cogs_dir}")
            
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    cog_path = f'cogs.{filename[:-3]}'
                    await self.load_extension(cog_path)
                    logger.info(f'Loaded cog: {filename[:-3]}')
                except Exception as e:
                    logger.error(f'Failed to load cog {filename}: {str(e)}')

        try:
            self.add_view(TicketControlView())
            logger.info("Persistent Ticket buttons loaded")
        except ImportError as e:
            logger.error(f"Failed to import TicketControlView or failed to load persistent buttons")
        
        # Sync commands with guild
        try:
            guild = discord.Object(id=self.guild_id)

            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f'Synced commands to guild {self.guild_id}')
        except Exception as e:
            logger.error(f'Error syncing commands to guild - {e}')

    async def close(self):
        try:
            if self.counting_db and getattr(self.counting_db, "db", None):
                await self.counting_db.db.close()
                logger.info("Counting database closed")

            if self.ticket_db and getattr(self.ticket_db, "db", None):
                await self.ticket_db.db.close()
                logger.info("Ticket database connection closed")
        except Exception as e:
            logger.critical(f"Error closing database connections: {e}")
        await super().close()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        
        # Setup logs channel
        try:
            self.logs_channel = self.get_channel(self.logs_channel_id)
            if self.logs_channel is None:
                self.logs_channel = await self.fetch_channel(self.logs_channel_id)
            logger.info(f'Synced to logs channel: {self.logs_channel.name}')
        except Exception as e:
            logger.error(f'Error syncing to logs channel - {e}')
        #END setup logs channel
        
        # Setup events channel
        try:
            self.events_channel = self.get_channel(self.events_channel_id)
            if self.events_channel is None:
                self.events_channel = await self.fetch_channel(self.events_channel_id)
            logger.info(f'Synced to events channel: {self.events_channel.name}')
        except Exception as e:
            logger.error(f'Error syncing event channel - {e}')
        #END setup events channel

        # Setup general channel
        try:
            self.general_channel = self.get_channel(self.general_channel_id)
            if self.general_channel is None:
                self.general_channel = await self.fetch_channel(self.general_channel_id)
            logger.info(f'Synced to events channel: {self.general_channel.name}')
        except Exception as e:
            logger.error(f'Error syncing event channel - {e}')
        #END setup general channel

         # Setup supersecret_general channel
        try:
            self.supersecret_general = self.get_channel(self.supersecret_general_channel_id)
            if self.supersecret_general is None:
                self.supersecret_general = await self.fetch_channel(self.supersecret_general_channel_id)
            logger.info(f'Synced to events channel: {self.supersecret_general.name}')
        except Exception as e:
            logger.error(f'Error syncing event channel - {e}')
        #END setup supersecret_general channel

        # Setup supersecret_general channel
        try:
            self.secret_general_channel = self.get_channel(self.secret_general_channel_id)
            if self.secret_general_channel is None:
                self.secret_general_channel = await self.fetch_channel(self.secret_general_channel_id)
            logger.info(f'Synced to events channel: {self.secret_general_channel.name}')
        except Exception as e:
            logger.error(f'Error syncing event channel - {e}')
        #END setup supersecret_general channel

        # Setup counting_channel_id channel
        try:
            self.counting_channel = self.get_channel(self.counting_channel_id)
            if self.counting_channel is None:
                self.counting_channel = await self.fetch_channel(self.counting_channel_id)
            logger.info(f'Synced to events channel: {self.counting_channel.name}')
        except Exception as e:
            logger.error(f'Error syncing event channel - {e}')
        #END setup counting_channel_id channel
        
            
    async def on_message(self, message):
        if message.author == self.user:
            return
            
        # Process commands from messages (needed for prefix commands)
        await self.process_commands(message)

async def main():
    bot = BanditBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
