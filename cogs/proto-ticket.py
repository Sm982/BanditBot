import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from logger import logger

class ProtoTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @app_commands.command(name="proticket", description="Create a support ticket")
    async def proticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Ticket #xxxxxxx",
            description="",
            color=banditColor
        )
        embed.add_field(name="Notice", value="This conversation is logged. After this ticket has been closed, a transcript will be saved.", inline=False)
        embed.add_field(name="Ticket handled by", value=f"claimed-user", inline=False)
        embed.timestamp = discord.utils.utcnow()

        view = TicketControlView(embed)

        await interaction.response.send_message(embed=embed, view=view)


class TicketControlView(discord.ui.View):
    def __init__(self, embed):
        super().__init__(timeout=None)
        self.embed = embed
    
    @discord.ui.button(label="Claim ticket", style=discord.ButtonStyle.green, emoji="⭐")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any (role.name == 'Bandits Admins' for role in interaction.user.roles):
            await interaction.response.send_message("Only Admins can claim tickets!", ephemeral = True)
            return
        
        self.embed.set_field_at(1, name="Ticket handled by", value=f"{interaction.user.display_name}", inline = False)
        await interaction.response.edit_message(embed=self.embed, view=self)
        await interaction.followup.send(f"Ticket claimed by {interaction.user.display_name}")


async def setup(bot):
    await bot.add_cog(ProtoTicket(bot), guilds=[discord.Object(id=bot.guild_id)])