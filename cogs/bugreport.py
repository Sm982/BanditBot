import discord
from discord import app_commands
from discord.ext import commands
from discord import SelectOption, TextStyle
from discord.ui import Select, View, Modal, TextInput
from logger import logger

# User inputs command /bugreport , opens modal with title and description, title and description gets sent to user sillymonkey982 ( CREATOR_USER_ID )

class bugreportCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    class BugReportModal(Modal):
        def __init__(self, cog):
            super().__init__(title="Create Bug Report")
            self.cog = cog
            
            self.title_input = TextInput(
                label="Bug Report Title",
                placeholder="Enter a title for your bug report",
                style=TextStyle.short,
                required=True,
                max_length=100
            )
            
            self.content_input = TextInput(
                label="Bug Report Content",
                placeholder="Enter a full description, alongside replication steps here.",
                style=TextStyle.long,
                required=True,
                max_length=2000
            )
            
            self.add_item(self.title_input)
            self.add_item(self.content_input)
        
        async def on_submit(self, interaction: discord.Interaction):
            user = await self.cog.bot.fetch_user(self.cog.bot.creator_user_id)
            
            embed = discord.Embed(
                title=f"Bug Report: {self.title_input.value}",
                description=f"{self.content_input.value}",
                color=self.cog.bot.banditColor
            )
            embed.set_footer(text=f"Reported by {interaction.user.name} ({interaction.user.id})")
            
            await user.send(embed=embed)
            await interaction.response.send_message("Bug report has been successfully sent! Thanks for your report!", ephemeral=True)
    
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
            logger.info(f'User {interaction.user.display_name} attempted to execute a command however did not have the correct permissions.')
        else:
            if interaction.response.is_done():
                await interaction.followup.send(f"An error occurred: {str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            logger.error(f'Error in command: {str(error)}')
    
    @app_commands.command(name="bugreport", description="Admins can report BanditBot bugs to a special place!")
    @app_commands.checks.has_any_role('Bandits Admins')
    async def report(self, interaction: discord.Interaction):
        await interaction.response.send_modal(bugreportCommand.BugReportModal(self))

async def setup(bot):
    await bot.add_cog(bugreportCommand(bot), guilds=[discord.Object(id=bot.guild_id)])