import discord
import time
from discord import app_commands
from discord.ext import commands

class commNightCMD(commands.Cog):
    global banditColor
    banditColor = 0x0a8888
    def __init__(self, bot):
        self.bot = bot
        
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
            
    @app_commands.command(name="communitynight", description="Schedule a community night")
    @commands.has_any_role('SillyMonkey')
    async def scheduler(self, interaction: discord.Interaction):
        await interaction.response.send_message("Sure", ephemeral=True)
        #Schedule community night command here
        embed = discord.Embed(
            title="Bandit Bot Info",
            color=banditColor
        )
        embed.add_field(name="Python Version", value="Community", inline=True)
        if self.bot.events_channel:
            await self.bot.events_channel.send(embed=embed)
     

async def setup(bot):
    await bot.add_cog(commNightCMD(bot), guilds=[discord.Object(id=bot.guild_id)])