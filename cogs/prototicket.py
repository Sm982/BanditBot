import discord
import re
import asyncio
from collections import defaultdict
from discord import app_commands
from discord.ext import commands
from discord import Color
from logger import logger

class ProtoTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state_loaded = False



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

    async def load_state(self):
        if not self.state_loaded: 
            state = await self.bot.ticket_db.initialize()
            self.state_loaded = True

    @app_commands.command(name="add2ticket", description="Add a user to a ticket")
    async def add2ticket(self, interaction: discord.Interaction, user: discord.user):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
            return
        
        channel = interaction.channel
        user_id = user.id

        await channel.set_permissions(user_id, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"Added <@{user_id}> to channel", ephemeral=True)


    @app_commands.command(name="proticket", description="Create a support ticket")
    async def proticket(self, interaction: discord.Interaction):
        ticketNumber = await self.bot.ticket_db.create_ticket(
            creator_user_id=interaction.user.id,
            created_at=discord.utils.utcnow().isoformat()
        )
        staff_role_id= 1044403662996373609

        if ticketNumber is None:
            await interaction.response.send_message("Failed to create ticket. Please try again.", ephemeral=True)
            return
        
        guild = interaction.guild
        channelOverwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(staff_role_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"Ticket #{ticketNumber}", overwrites=channelOverwrites)

        embed = discord.Embed(
            title=f"Ticket #{ticketNumber}",
            description="",
            color=banditColor
        )
        embed.add_field(name="Notice", value="This conversation is logged. After this ticket has been closed, a transcript will be saved.", inline=False)
        embed.add_field(name="Ticket handled by", value=f"claimed-user", inline=False)
        embed.timestamp = discord.utils.utcnow()

        view = TicketControlView()
        await channel.send(embed=embed, view=view)

        thread = await channel.create_thread(name=f"Staff-#{ticketNumber}", type=discord.ChannelType.private_thread, reason=f"Staff discussion for ticket #{ticketNumber}")
        staff_role_id= 1044403662996373609
        staff_role = discord.utils.get(guild.roles, id=staff_role_id)
        if staff_role:
        
            for member in staff_role.members:
                try:
                    await thread.add_user(member)
                except discord.HTTPException:
                    pass  # Skip if user can't be added
        
        await thread.send(f"{staff_role.mention} 🔒 **Staff Only Discussion**\nThis is a private discussion thread for Ticket #{ticketNumber}")
        await interaction.response.send_message("Ticket created", ephemeral=True)


class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim ticket", style=discord.ButtonStyle.green, emoji="⭐", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any (role.name == 'Bandits Admins' for role in interaction.user.roles):
            await interaction.response.send_message("Only Admins can claim tickets!", ephemeral = True)
            return
        
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]

            ticket_number = int(embed.title.split('#')[1])

            result = await interaction.client.ticket_db.check_if_claimed_ticket(ticket_number)
            if result and result[0] is not None:
                await interaction.response.send_message("This ticket has already been claimed!", ephemeral=True)
                return
            
            button.disabled = True
            button.label = "Claimed!"
            button.style = discord.ButtonStyle.gray
            button.emoji= "✅"
            
            embed.set_field_at(1, name="Ticket handled by", value=f"<@{interaction.user.id}>", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"Ticket claimed by {interaction.user.display_name}")
            await interaction.client.ticket_db.assign_ticket(ticket_number, interaction.user.id)

    @discord.ui.button(label="Close ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.followup.send(f"Ticket closed")


async def setup(bot):
    await bot.add_cog(ProtoTicket(bot), guilds=[discord.Object(id=bot.guild_id)])