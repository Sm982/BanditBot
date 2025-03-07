import discord
from logger import logger
from discord import app_commands
from discord.ext import commands

class GeneralCommands(commands.Cog):
    global banditColor
    banditColor = 0x0a8888
    def __init__(self, bot):
        self.bot = bot
        
    # Error handling method for application commands
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
    
    @app_commands.command(name="hello", description="Bandit Bot says hello!")
    async def say_hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hi there! {interaction.user}', ephemeral=True)
        logger.info(f'BanditBot replied with Hello to {interaction.user}')
            
    @app_commands.command(name="printer", description="Bandit Bot repeats your message")
    @app_commands.checks.has_any_role('Bandits Admins') 
    async def printer(self, interaction: discord.Interaction, printer: str):
        await interaction.response.send_message(printer, ephemeral=False)
        
        # Log to the logs channel if available
        if self.bot.logs_channel:
            embed = discord.Embed(
                title=f"{interaction.user.display_name}",
                color=banditColor,
                description=f"{interaction.user.display_name} forced BanditBot to send a message with content - {printer}"
            )
            await self.bot.logs_channel.send(embed=embed)
        
        logger.info(f'User {interaction.user.display_name} forced BanditBot to send a message with the content - {printer}')

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot), guilds=[discord.Object(id=bot.guild_id)])