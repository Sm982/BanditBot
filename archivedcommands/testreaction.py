import discord
from discord import app_commands
from discord.ext import commands
from logger import logger

class ReactionMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitored_message_id = None
        self.monitored_channel_id = None

    @app_commands.command(name="setup_reaction_monitor", description="Send a monitored embed to a channel")
    @app_commands.checks.has_any_role('Bandits Admins')
    @app_commands.describe(channel="The channel to send the embed to", title="Title of the embed", description="Description of the embed", emoji="The emoji to monitor")
    async def setup_monitor(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str, emoji : str = "✅"):
        embed = discord.Embed(title=title, description=description, color=self.bot.banditColor)
        embed.set_footer(text="React to this message!")

        try: 
            message = await channel.send(embed=embed)

            await message.add_reaction(emoji)

            self.monitored_message_id = message.id
            self.monitored_channel_id = channel.id

            await interaction.response.send_message("Reaction monitor setup!", ephemeral=True)
            logger.info(f"User {interaction.user.display_name} setup reaction monitor in channel {channel.name}")

        except Exception as e:
            await interaction.response.send_message("Failed to setup reaction monitor", ephemeral=True)
            logger.info(f"Failed to setup reaction monitor: {str(e)}")

    
    @app_commands.command(name="clear_reaction_monitor", description="Clear the currrent reaction monitor")
    @app_commands.checks.has_any_role('Bandits Admins')
    async def clear_monitor(self, interaction: discord.Interaction):
        if self.monitored_message_id:
            old_msg_id = self.monitored_message_id
            self.monitored_message_id = None
            self.monitored_channel_id = None
            await interaction.response.send_message("Reaction monitored cleared", ephemeral=True)
            logger.info(f"User {interaction.user.display_name} cleared reaction monitor")
        else:
            await interaction.response.send_message("No active reaction monitor to clear", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        
        if payload.message_id != self.monitored_message_id:
            return
        
        user = await self.bot.fetch_user(payload.user_id)

        logger.info(f"User {user.name} (ID: {user.id}) reacted with {payload.emoji} to monitored message")

        try:
            channel = self.bot.get_channel(payload.channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(payload.channel_id)

            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, user)

        except Exception as e:
            logger.error(f"Failed to remove reaction: {str(e)}")

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
            logger.info(f'User {interaction.user.display_name} attempted to execute a command however did not have the correct permissions.')
        else:
            if interaction.response.is_done():
                await interaction.followup.send(f"An error occurred: {str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            logger.error(f'Error in command: {str(error)}')


async def setup(bot):
    await bot.add_cog(ReactionMonitor(bot), guilds=[discord.Object(id=bot.guild_id)])