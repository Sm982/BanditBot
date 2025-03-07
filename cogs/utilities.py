import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from logger import logger
import platform
import time

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    global banditColor
    banditColor = 0x0a8888

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
            logger.info(f'User {interaction.user.display_name} attempted to execute a command however did not have the correct permissions.')
        else:
            # Handle other errors
            if interaction.response.is_done():
                await interaction.followup.send(f"An error occurred: {str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            logger.error(f'Error in command: {str(error)}')
        
    @app_commands.command(name="info", description="Check the bot's uptime and latency")
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
        logger.info(f'User {interaction.user.display_name} requested the Bot\'s uptime and latency')
        
    @app_commands.command(name="about", description="Learn all about BanditBot!")
    async def about(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'SillyMonkey hasn\'t finished writing this command yet!')

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot), guilds=[discord.Object(id=bot.guild_id)])