import discord
import re
import asyncio
import os
from collections import defaultdict
from discord import app_commands
from discord.ext import commands
from discord import Color
from logger import logger
from datetime import datetime


async def closeTicket(interaction: discord.Interaction):
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
        
    channel = interaction.channel    
    channelName = interaction.channel.name
    ticketNumber = channelName.removeprefix("ticket-")

    await interaction.response.send_message(f"Closing ticket #{ticketNumber}")

    currentTime = datetime.now()
    await interaction.client.ticket_db.update_ticket_status(ticketNumber, "CLOSED", currentTime)
    user = interaction.user

    # Create transcript - simple one-liner approach
    transcript_file = f"transcripts/ticket-{ticketNumber}.txt"
    os.makedirs("transcripts", exist_ok=True)
    
    with open(transcript_file, 'w', encoding='utf-8') as file:
        file.write(f"Ticket #{ticketNumber} Transcript\n{'='*40}\n\n")
        
        async for message in channel.history(limit=None, oldest_first=True):
            if not message.author.bot:  # Skip bot messages
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"[{timestamp}] {message.author.display_name}: {message.content}\n")

    await asyncio.sleep(2)
    creator_user_id = await interaction.client.ticket_db.get_ticket_creator(ticketNumber)
    if creator_user_id:
        try:
            creator = await interaction.client.fetch_user(creator_user_id)
            await creator.send(
                f"Your ticket #{ticketNumber} has been closed. Here's the transcript:",
                file=discord.File(transcript_file)
            )
            logger.info(f"Sent transcript for ticket #{ticketNumber} to user {creator_user_id}")
        except discord.errors.Forbidden:
            logger.warning(f"Could not send transcript to user {creator_user_id} - DMs disabled")
        except Exception as e:
            logger.error(f"Error sending transcript to user {creator_user_id}: {e}")
    
    await interaction.channel.delete(reason="Test")

class ProtoTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state_loaded = False
        self.banditColor = bot.banditColor

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

    async def create_ticket_channel(self, interaction: discord.Interaction):
        guild = interaction.guild
        staff_role_id = self.bot.staff_role_id

        await interaction.response.defer(ephemeral=True)

        ticketNumber = await self.bot.ticket_db.create_ticket(
            creator_user_id= interaction.user.id,
            created_at= discord.utils.utcnow().isoformat()
        )

        if ticketNumber is None:
            await interaction.response.send_message("Failed to create ticket. Please try again.", ephemeral=True)
            return
        
        channelOverwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(staff_role_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(f"Ticket #{ticketNumber}", overwrites=channelOverwrites)

        thread = await channel.create_thread(name=f"Staff-#{ticketNumber}", type=discord.ChannelType.private_thread, reason=f"Staff discussion for ticket #{ticketNumber}")
        staff_role = discord.utils.get(guild.roles, id=staff_role_id)
        if staff_role:
            for member in staff_role.members:
                try:
                    await thread.add_user(member)
                except discord.HTTPException:
                    pass  # Skip if user can't be added
        
        await thread.send(f"{staff_role.mention} 🔒 **Staff Only Discussion**\nThis is a private discussion thread for Ticket #{ticketNumber}")

        # create the embed
        embed = discord.Embed(
            title=f"Ticket #{ticketNumber}",
            description="",
            color=self.banditColor
        )

        embed.add_field(name="Notice", value="This conversation is logged. After this ticket has been closed, a transcript will be saved.", inline=False)
        embed.add_field(name="Ticket handled by", value=f"claimed-user", inline=False)
        embed.set_footer(text="‎", icon_url="https://cdn.discordapp.com/avatars/1345267097411911690/ed77459d3af253c42234f6ab94bb9b2d.webp?size=160")
        embed.timestamp = discord.utils.utcnow()

        # add the button then send the message
        view = TicketControlView()
        await channel.send(embed=embed, view=view)

        await interaction.followup.send(f"Ticket <#{channel.id}> created!", ephemeral=True)

    @app_commands.command(name="gettickettranscript", description="Get a transcript from a ticket")
    @app_commands.checks.has_any_role('Bandits Admins')
    async def gettickettranscript(self, interaction: discord.Interaction, ticknum: str):
        ticketPrefix = f"ticket-{ticknum}"
        guild = interaction.guild

        if not os.path.exists(f"transcripts/ticket-{ticknum}.txt"):
            await interaction.response.send_message("File doesn't exist.", ephemeral=True)
            return

        await interaction.response.send_message("Here is your ticket transcript!", file=discord.File(f"transcripts/{ticketPrefix.txt}"))

    @app_commands.command(name="ticketlisten", description="Set the listening channel for the ticket embed")
    async def ticketlistener(self, interaction: discord.Interaction):
        if interaction.user.id != self.bot.creator_user_id:
            await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Ticket",
            description="To create a ticket use the Create ticket button",
            color=self.bot.banditColor
        )
        embed.set_footer(text="BanditBot", icon_url="https://cdn.discordapp.com/avatars/1345267097411911690/ed77459d3af253c42234f6ab94bb9b2d.webp?size=160")

        view = TicketCreateControlView()
        await interaction.channel.send(embed=embed, view=view)

    @app_commands.command(name="add", description="Add a user to a ticket")
    @app_commands.checks.has_any_role('Bandits Admins')
    async def addusertoticket(self, interaction: discord.Interaction, user: discord.User, channel: discord.TextChannel):
        guild = interaction.guild

        if not channel.name.startswith("ticket-"):
            await interaction.response.send_message("Either that ticket doesn't exist or you entered a regular channel!", ephemeral=True)
            return
        
        await channel.set_permissions(user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"Added <@{user.id}> to ticket <#{channel.id}>", ephemeral=True)

    @app_commands.command(name="closeticket", description="Close the current ticket you're working in")
    async def closecurrentticket(self, interaction: discord.Interaction):
        await closeTicket(interaction)

    @app_commands.command(name="proticket", description="Create a support ticket")
    async def create_the_ticket(self, interaction: discord.Interaction):
        await self.create_ticket_channel(interaction)

class TicketCreateControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    
    @discord.ui.button(label="Create a Ticket", style=discord.ButtonStyle.green, emoji="📩", custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('ProtoTicket')
        await cog.create_ticket_channel(interaction)

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
            await interaction.followup.send(f"Ticket claimed by <@{interaction.user.id}>")
            await interaction.client.ticket_db.assign_ticket(ticket_number, interaction.user.id)

    @discord.ui.button(label="Close ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await closeTicket(interaction)


async def setup(bot):
    await bot.add_cog(ProtoTicket(bot), guilds=[discord.Object(id=bot.guild_id)])