import discord
import time
from discord import app_commands
from discord.ext import commands

class commNightCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.tree.error
    async def on_app_command_error(interaction,error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
            
    @app_commands.command(name="communitynight", description="Schedule a community night")
    @commands.has_any_role('SillyMonkey')
    async def scheduler(self, interaction: discord.Interaction):
        await interaction.response.send_message("Sure", ephemeral=True)
        #Schedule community night command here
     

async def setup(bot):
    await bot.add_cog(commNightCMD(bot), guilds=[discord.Object(id=bot.guild_id)])