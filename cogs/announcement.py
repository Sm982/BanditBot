import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from logger import logger
import time

# Plan for the bot is to have ephemeral select drop down menus as ephemeral and then 

class announcementCommand(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.start_time = time.time()

    global banditColor
    banditColor = 0x0a8888
    
    class ChannelSelectView(View):
        def __init__(self, cog):
            super().__init__(timeout=60)
            self.cog = cog
            
        self.channel_select = Select(
            placeholder="Please select an option...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="General", description="Main General Channel", emoji="", value=f"{self.general_channel_id}"),
                discord.SelectOption(label="Events", description="Main Events Channel", emoji="", value=f"{self.events_channel_id}"),
                discord.SelectOption(label="SMGeneral", description="Admin Chat Channel", emoji="", value=f"{self.supersecret_general_channel_id}"),
                discord.SelectOption(label="MGeneral", description="Mods Chat Channel", emoji="", value=f"{self.secret_general_channel_id}")
            ]
        )
        
        self.channel_select.callback = self.channel_selected
        self.add_item(self.channel_select)
        
        async def channel_selected(self, interaction: discord.Interaction):
            selected_chanel_attr= self.channel_select.values[0]
            self.selected_channel_id = getattr(self.cog, selected_chanel_attr)
            await interaction.response.send_message("fYou selected a channel. Now decide if you want to annoy everyone:", view=announcementCommand.MentionSelectView(self.cog, self.selected_channel_id), ephemeral=True)

    class MentionSelectView(View):
        
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

    @app_commands.command(name="announce", description="Announce a message to the world!")
    @app_commands.checks.has_any_role('Bandits Admins')
    async def announce(self, interaction: discord.Interaction):
        



async def setup(bot):
    await bot.add_cog(announcementCommand(bot), guilds=[discord.Object(id=bot.guild_id)])