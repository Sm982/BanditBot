import discord
from discord import app_commands
from discord.ext import commands
import datetime
import time
import pytz

class scheduleStreamCMD(commands.cog):
    global banditColor
    banditColor = 0x0a8888

    # Error handling method for slash commands
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
        else:
            if interaction.response.is_done():
                await interaction.followup.send(f"An error occurred:{str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            print(f"Error in command: {str(error)}")

    @app_commands.command(name="schedulestreams", description="Schedule Bandit's streams for the week")
    @commands.has_any_role("Bandits Admins")
    async def schedulestream(self, interaction: discord.Interaction):
        print('test')


async def setup(bot):
    await bot.add_cog(scheduleStreamCMD(bot), guilds=[discord.Object(id=bot.guild_id)])