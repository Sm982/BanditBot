import discord
from discord import app_commands
from discord.ext import commands
import platform
import time

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        
    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency is {latency}ms")
        
    @app_commands.command(name="uptime", description="Check how long the bot has been running")
    async def uptime(self, interaction: discord.Interaction):
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        embed = discord.Embed(
            title="Bandit Bot Uptime",
            color=discord.Color.blue()
        )
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="botinfo", description="Get information about the bot")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bandit Bot Info",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot), guilds=[discord.Object(id=bot.guild_id)])