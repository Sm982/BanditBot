import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
import platform
import time

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    global banditColor
    banditColor = 0x0a8888

    # Error handling method for application commands
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
        else:
            # Handle other errors
            if interaction.response.is_done():
                await interaction.followup.send(f"An error occurred: {str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            print(f"Error in command: {str(error)}")
        
    @app_commands.command(name="info", description="Check the bot's latency")
    @app_commands.checks.has_any_role('Bandits Admins') 
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{hours}h {minutes}m {seconds}s"

        embed = discord.Embed(
            title="Bandit Bot Info",
            color=banditColor
        )
        embed.add_field(name="Latency", value=str(latency), inline=True)
        embed.add_field(name="Uptime", value=uptime_str + "ms", inline=True)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="botinfo", description="Get information about the bot")
    @app_commands.checks.has_any_role('SillyMonkey') 
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bandit Bot Info",
            color=banditColor
        )
        
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot), guilds=[discord.Object(id=bot.guild_id)])