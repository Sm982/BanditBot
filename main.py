import discord
import os
import asyncio
import importlib.util
from logger import logger
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD'))
LOGS_CHANNEL_ID = int(os.getenv('DISCORD_GUILD_LOGS_CHANNEL'))
EVENTS_CHANNEL_ID = int(os.getenv('DISCORD_EVENTS_CHANNEL'))
GENERAL_CHANNEL_ID = int(os.getenv('DISCORD_GENERAL_CHANNEL'))
SUPERSECRET_CHANNEL_ID = int(os.getenv('DISCORD_SUPERS_CHANNEL'))
SECRET_CHANNEL_ID = int(os.getenv('DISCORD_SECRET_CHANNEL'))

class BanditBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents)
        
        # Store important IDs
        self.guild_id = GUILD_ID
        self.logs_channel_id = LOGS_CHANNEL_ID
        self.events_channel_id = EVENTS_CHANNEL_ID
        self.general_channel_id = GENERAL_CHANNEL_ID #
        self.supersecret_general_channel_id = SUPERSECRET_CHANNEL_ID
        self.secret_general_channel_id = SECRET_CHANNEL_ID
        self.logs_channel = None
        self.events_channel = None
        
    async def setup_hook(self):
        # Load all cogs
        logger.info("Loading cogs...")
        cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
        
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
        
        # Sync commands with guild
        try:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f'Synced commands to guild {self.guild_id}')
        except Exception as e:
            logger.error(f'Error syncing commands to guild - {e}')
            
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