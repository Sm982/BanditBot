import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

### LOAD DISCORD BOT TOKEN ###
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS_ID = int(os.getenv('DISCORD_GUILD'))
BB_LOGS_ID = str(os.getenv('DISCORD_GUILD_LOGS_CHANNEL'))
### END DISCORD BOT LOAD ###

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')
        # START DEFINING THE LOGS CHANNEL FOR BOT #
        global BB_LOGS
        BB_LOGS = client.get_channel(BB_LOGS_ID)
        if BB_LOGS is None:
            BB_LOGS = await client.fetch_channel(BB_LOGS_ID)
        # END DEFINING THE LOGS CHANNEL FOR BOT #
        # DEFINE GUILD ID #

        try:
            guild = discord.Object(id=GUILDS_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')
        except Exception as e:
            print(f'Error syncing commands to guild - {e}')
            

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there! {message.author}')

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="?", intents=intents)

GUILD_ID = discord.Object(id=GUILDS_ID)

### COMMAND HANDLING ###

@client.tree.command(name="hello", description="Bandit Bot says hello!", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi there! {interaction.user}')
    print(f'BanditBot replied with Hello to {interaction.user}')

@client.tree.command(name="printer", description="Bandit Bot repeats your message", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)
    await BB_LOGS.send(f'User {interaction.user} forced BanditBot to send a message with content - {printer}')
    print(f'User {interaction.user} forced BanditBot to send a message with content - {printer}')

client.run(TOKEN)