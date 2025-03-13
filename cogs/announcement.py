import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from discord import SelectOption, TextStyle
from discord.ui import Select, View, Modal, TextInput
from logger import logger
import time


class announcementCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        # Channel IDs are available on the bot object, not directly on the cog

    global banditColor
    banditColor = 0x0a8888
    
    class ChannelSelectView(View):
        def __init__(self, cog):
            super().__init__(timeout=60)
            self.cog = cog
            
            # Create dropdown with channel options
            self.channel_select = Select(
                placeholder="Please select an option...",
                min_values=1,
                max_values=1,
                options=[
                    SelectOption(label="General", description="Main General Channel", value="general_channel_id"),
                    SelectOption(label="Events", description="Main Events Channel", value="events_channel_id"),
                    SelectOption(label="SMGeneral", description="Admin Chat Channel", value="supersecret_general_channel_id"),
                    SelectOption(label="MGeneral", description="Mods Chat Channel", value="secret_general_channel_id")
                ]
            )
            
            self.channel_select.callback = self.channel_selected
            self.add_item(self.channel_select)
        
        async def channel_selected(self, interaction: discord.Interaction):
            # Get the attribute name from the selection
            selected_channel_attr = self.channel_select.values[0]
            
            # Get the actual channel ID from the bot object (not the cog)
            self.selected_channel_id = getattr(self.cog.bot, selected_channel_attr)
            
            await interaction.response.send_message(
                "You selected a channel. Now decide if you want to annoy everyone:", 
                view=announcementCommand.MentionSelectView(self.cog, self.selected_channel_id), 
                ephemeral=True
            )

    class MentionSelectView(View):
        def __init__(self, cog, selected_channel_id):
            super().__init__(timeout=60)
            self.cog = cog
            self.selected_channel_id = selected_channel_id

            self.mention_select = Select(
                placeholder="Please choose an option...",
                min_values=1,
                max_values=1,
                options=[
                    SelectOption(label="No mentions", description="Don't tag everyone", value="notag"),
                    SelectOption(label="@everyone", description="Tag everyone in the server", value="tageveryone"),
                    SelectOption(label="@here", description="Tag active members only", value="here")
                ]
            )

            self.mention_select.callback = self.mention_selected
            self.add_item(self.mention_select)

        async def mention_selected(self, interaction: discord.Interaction):
            selected_mention = self.mention_select.values[0]
            await interaction.response.send_modal(
                announcementCommand.AnnouncementModal(self.cog, self.selected_channel_id, selected_mention)
            )
    
    class AnnouncementModal(Modal):
        def __init__(self, cog, channel_id, mention_type):
            super().__init__(title="Create Announcement")
            self.cog = cog
            self.channel_id = channel_id
            self.mention_type = mention_type

            # Title input
            self.title_input = TextInput(
                label="Announcement Title",
                placeholder="Enter a title for your announcement",
                style=TextStyle.short,
                required=True,
                max_length=100
            )
        
            # Content input - multiline for longer messages
            self.content_input = TextInput(
                label="Announcement Content",
                placeholder="Enter the full announcement message here",
                style=TextStyle.long,
                required=True,
                max_length=2000
            )
        
            # Add inputs to the modal
            self.add_item(self.title_input)
            self.add_item(self.content_input)
            
        async def on_submit(self, interaction: discord.Interaction):
            channel = self.cog.bot.get_channel(self.channel_id)

            if not channel:
                await interaction.response.send_message("Could not find the selected channel.", ephemeral=True)
                return
                
            # Create embed
            embed = discord.Embed(
                title=self.title_input.value,
                description=self.content_input.value,
                color=Color(banditColor)  # Using your custom color
            )
            embed.set_footer(text=f"Announcement by {interaction.user.display_name}")
        
            # Prepare mention string
            mention_str = ""
            if self.mention_type == "tageveryone":
                mention_str = "@everyone"
            elif self.mention_type == "here":
                mention_str = "@here"
        
            # Send confirmation to user
            await interaction.response.send_message(
                f"Your announcement has been sent to the selected channel!",
                ephemeral=True
            )
            await channel.send(content=mention_str, embed=embed)
        
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
        await interaction.response.send_message(
            "Let's create an announcement. First, select a channel:",
            view=self.ChannelSelectView(self),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(announcementCommand(bot), guilds=[discord.Object(id=bot.guild_id)])