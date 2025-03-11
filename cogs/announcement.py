import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from logger import logger
import time

# Plan for the bot is to have a modal with a list of channels to announce
# inside of. Option to tag everyone or not
# text box with message

class AnnouncementModal(discord.ui.Modal, title="Send an Announcement"):


    #Channel list
    channelList = discord.ui.Select(
        placeholder="Choose a channel",
        options=[
            discord.SelectOption(label="important", description="", emoji="📝", value="important"),
            discord.SelectOption(label="general", description="", emoji="📝", value="general")
        ],
        required=True
    )

    #Tag everyone?
    everyoneQuestion = discord.ui.Select(
        placeholder="Would you like to tag everyone or not?",
        options=[
            discord.SelectOption(label="Yes", description="You will be tagging everyone in the server", emoji="❓", value="affirm"),
            discord.SelectOption(label="No", description="You will NOT be tagging everyone in teh server", emoji="❓", value="negative")
        ],
        required=True
    )

    #Text input for the announcement
    announceMsg = discord.ui.TextInput(
        label="Your announcement message",
        placeholder="Provide a message...",
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_item(self.channelList)
        self.add_item(self.everyoneQuestion)
        self.add_item(self.announceMsg)

    async def on_submit(self, interaction: discord.Interaction):
        selected_channel = self.channelList.values[0]
        selected_everyone = self.everyoneQuestion.values[0]
        announce_text = self.announceMsg.value

        await interaction.response.send_message(
            f"Your announcement has been sent!\n"
            f"Selected Channel: {selected_channel}\n"
            f"Tagging everyone? {selected_everyone}\n"
            f"Announcement message: {announce_text}",
            ephemeral=True
        )

        embed = discord.Embed(
            title="Announcement!!",
            description=f"{announce_text}",
            color=banditColor
        )
        try:
            match selected_channel:
                case "important":
                    channel = await self.bot.fetch_channel(1044403663357104178)
                    await channel.send("@everyone", embed=embed)
                case "general":
                    channel = await self.bot.fetch_channel(1044403663357104184)
                    await channel.send("@everyone", embed=embed)
        except discord.errors.NotFound:
            # This handles if the channel doesn't exist
            logger.error(f"Channel with ID {channel_id} not found")
            await interaction.followup.send(
                f"Error: Could not find the channel to send the announcement to.",
                ephemeral=True
            )
        except discord.errors.Forbidden:
            # This handles if the bot doesn't have permission
            logger.error(f"Bot doesn't have permission to send messages in channel {channel_id}")
            await interaction.followup.send(
                f"Error: I don't have permission to send messages in that channel.",
                ephemeral=True
            )
        except Exception as e:
            # General exception handler for any other issues
            logger.error(f"Error sending announcement: {str(e)}")
            await interaction.followup.send(
                f"An unexpected error occurred while sending the announcement: {str(e)}",
                ephemeral=True
            )




class announcementCommand(commands.Cog):
    def __init__(self,bot):
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

    @app_commands.command(name="announce", description="Announce a message to the world!")
    @app_commands.checks.has_any_role('Bandits Admins')
    async def announce(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AnnouncementModal())



async def setup(bot):
    await bot.add_cog(announcementCommand(bot), guilds=[discord.Object(id=bot.guild_id)])