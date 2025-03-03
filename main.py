import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD'))
LOGS_CHANNEL_ID = int(os.getenv('DISCORD_GUILD_LOGS_CHANNEL'))

class BanditBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents)
        
        # Store important IDs
        self.guild_id = GUILD_ID
        self.logs_channel_id = LOGS_CHANNEL_ID
        self.logs_channel = None
        
    async def setup_hook(self):
        # Load all cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded cog: {filename[:-3]}')
        
        # Sync commands with guild
        try:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f'Synced commands to guild {self.guild_id}')
        except Exception as e:
            print(f'Error syncing commands to guild - {e}')
            
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        
        # Setup logs channel
        try:
            self.logs_channel = self.get_channel(self.logs_channel_id)
            if self.logs_channel is None:
                self.logs_channel = await self.fetch_channel(self.logs_channel_id)
            print(f'Synced to logs channel: {self.logs_channel.name}')
        except Exception as e:
            print(f'Error syncing to logs channel - {e}')
            
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