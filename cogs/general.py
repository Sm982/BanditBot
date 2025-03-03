import discord
from discord import app_commands
from discord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.tree.error
    async def on_app_command_error(interaction,error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
    
        
    @app_commands.command(name="hello", description="Bandit Bot says hello!")
    async def say_hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hi there! {interaction.user}')
        print(f'BanditBot replied with Hello to {interaction.user}', ephemeral=True)
        
        # Log to the logs channel if available
        if self.bot.logs_channel:
            await self.bot.logs_channel.send(f'Replied with hello to {interaction.user}')
            
    @app_commands.command(name="printer", description="Bandit Bot repeats your message")
    @commands.has_any_role('SillyMonkey')
    async def printer(self, interaction: discord.Interaction, printer: str):
        await interaction.response.send_message(printer, ephemeral=True)
        
        # Log to the logs channel if available
        if self.bot.logs_channel:
            await self.bot.logs_channel.send(f'User {interaction.user} forced BanditBot to send a message with content - {printer}')
        
        print(f'User {interaction.user} forced BanditBot to send a message with content - {printer}')

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot), guilds=[discord.Object(id=bot.guild_id)])