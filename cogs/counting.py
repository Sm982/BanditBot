import discord
import re
import asyncio
from collections import defaultdict
from logger import logger
from discord import app_commands
from discord.ext import commands

def is_user(user_id: int):
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == user_id
    return app_commands.check(predicate)

class CountingCog(commands.Cog):
   def __init__(self, bot):
       self.bot = bot
       self.current_count = 0
       self.last_user_id = None
       self.highest_count = 0
       self.state_loaded = False

       self.active_votes = {}
       self.vote_duration = 300
       self.required_votes = 2

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

   async def load_state(self):
       if not self.state_loaded:
           state = await self.bot.counting_db.get_counting_state(self.bot.guild_id)
           self.current_count = state['current_count']
           self.last_user_id = state['last_user_id']
           self.highest_count = state['highest_count']
           self.state_loaded = True

   async def save_state(self):
       await self.bot.counting_db.update_counting_state(
           self.bot.guild_id,
           self.current_count,
           self.last_user_id,
           self.highest_count
       )

   @commands.Cog.listener()
   async def on_ready(self):
       await self.load_state()
   
   @commands.Cog.listener()
   async def on_message(self, message):
       if message.author.bot:
           return
       
       if message.channel.id != self.bot.counting_channel_id:
           return
       
       content = message.content.strip()
       if not self.is_valid_number(content):
           await message.delete()
           return
       
       try:
           number = int(content)
       except ValueError:
           await message.delete()
           return
       
       expected_number = self.current_count + 1
       if number != expected_number:
           await self.reset_count(message.channel, f"{message.author.mention} broke the chain! Expected {expected_number}, got {number}")
           return
       
       if message.author.id == self.last_user_id:
           await self.reset_count(message.channel, f"{message.author.mention} posted twice in a row!")
           await message.delete()
           return
       
       self.current_count = number
       self.last_user_id = message.author.id

       if number > self.highest_count:
           self.highest_count = number
       
       await message.add_reaction("✅")
       await self.bot.counting_db.log_count(self.bot.guild_id, number, message.author.id)
       await self.save_state()

   def is_valid_number(self, content):
       return re.match(r'^\d+$', content) is not None
   
   async def reset_count(self, channel, reason):
       self.current_count = 0
       self.last_user_id = None

       embed = discord.Embed(
           title="Count Reset! 🔄",
           description=f"**Reason:** {reason}\n**Starting over from 0**",
           color=discord.Color.red()
       )
       await channel.send(embed=embed)
       await self.save_state()
   
   @app_commands.command(name="supercheatcount", description="Directy set the count")
   @is_user(764025944750948362)
   async def super_cheat_count(self, interaction: discord.Interaction, number: int):
       
       if number < 0:
           await interaction.response.send_message("❌ Count cannot be negative!", ephemeral=True)
           return
   
       old_count = self.current_count
       self.current_count = number
       self.last_user_id = None  # Reset last user so anyone can continue
   
       if number > self.highest_count:
           self.highest_count = number
   
       await self.save_state()
   
       embed = discord.Embed(
           title="🔧 Count Manually Set",
           description=f"Count changed from **{old_count}** to **{number}**",
           color=discord.Color.gold()
       )
   
       await interaction.response.send_message(embed=embed)
   
       # Notify the counting channel
       counting_channel = self.bot.get_channel(self.bot.counting_channel_id)
       if counting_channel:
           notify_embed = discord.Embed(
               title="🔧 Count Updated",
               description=f"Count has been manually set to **{number}**",
               color=discord.Color.gold()
           )
           await counting_channel.send(embed=notify_embed)

   @app_commands.command(name="cheatcounting", description="If for some reason, some accident ocurrs, cast a vote to reset the count to the previous save!")
   @app_commands.checks.has_any_role('Bandits Admins')
   async def cheat_count(self, interaction: discord.Interaction, reason: str = "Manual revert requested"):
       if self.bot.guild_id in self.active_votes:
           await interaction.response.send_message("❌ A vote is already in progress!", ephemeral=True)
           return
           
       last_count_data = await self.bot.counting_db.get_last_valid_count(self.bot.guild_id)
       if not last_count_data:
           await interaction.response.send_message("❌ No previous count found to revert to!", ephemeral=True)
           return
           
       embed = discord.Embed(
           title="🗳️ Count Revert Vote",
           description=f"**Reason:** {reason}\n**Current Count:** {self.current_count}\n**Revert to:** {last_count_data['count']}",
           color=discord.Color.orange()
       )
       embed.add_field(name="Votes Needed", value=f"{self.required_votes}", inline=True)
       embed.add_field(name="Time Limit", value=f"{self.vote_duration // 60} minutes", inline=True)
       embed.set_footer(text="React with ✅ to vote YES or ❌ to vote NO")
       
       await interaction.response.send_message(embed=embed)
       message = await interaction.original_response()
       
       await message.add_reaction("✅")
       await message.add_reaction("❌")
       
       self.active_votes[self.bot.guild_id] = {
           'message': message,
           'last_count': last_count_data,
           'reason': reason,
           'votes_yes': set(),
           'votes_no': set(),
           'started_by': interaction.user.id
       }
       
       asyncio.create_task(self._vote_timer(self.bot.guild_id))

   @commands.Cog.listener()
   async def on_reaction_add(self, reaction, user):
       if user.bot:
           return
           
       guild_id = reaction.message.guild.id if reaction.message.guild else None
       if guild_id not in self.active_votes:
           return
           
       vote_data = self.active_votes[guild_id]
       if reaction.message.id != vote_data['message'].id:
           return
           
       if str(reaction.emoji) == "✅":
           vote_data['votes_yes'].add(user.id)
           vote_data['votes_no'].discard(user.id)
       elif str(reaction.emoji) == "❌":
           vote_data['votes_no'].add(user.id)
           vote_data['votes_yes'].discard(user.id)
           
       if len(vote_data['votes_yes']) >= self.required_votes:
           await self._execute_revert(guild_id)
   
   async def _vote_timer(self, guild_id):
       await asyncio.sleep(self.vote_duration)
       
       if guild_id in self.active_votes:
           vote_data = self.active_votes[guild_id]
           
           embed = discord.Embed(
               title="🗳️ Vote Failed",
               description="Vote timed out without enough support.",
               color=discord.Color.red()
           )
           embed.add_field(name="Final Votes", value=f"✅ {len(vote_data['votes_yes'])} | ❌ {len(vote_data['votes_no'])}")
           
           await vote_data['message'].edit(embed=embed)
           del self.active_votes[guild_id]
   
   async def _execute_revert(self, guild_id):
       vote_data = self.active_votes[guild_id]
       last_count_data = vote_data['last_count']
       
       self.current_count = last_count_data['count']
       self.last_user_id = last_count_data['user_id']
       await self.save_state()
       
       embed = discord.Embed(
           title="✅ Count Reverted!",
           description=f"Count successfully reverted to **{last_count_data['count']}**",
           color=discord.Color.green()
       )
       embed.add_field(name="Final Votes", value=f"✅ {len(vote_data['votes_yes'])} | ❌ {len(vote_data['votes_no'])}")
       
       await vote_data['message'].edit(embed=embed)
       
       counting_channel = self.bot.get_channel(self.bot.counting_channel_id)
       if counting_channel:
           notify_embed = discord.Embed(
               title="🔄 Count Restored",
               description=f"Restored the count to **{last_count_data['count']}**\n**Reason:** {vote_data['reason']}",
               color=discord.Color.blue()
           )
           await counting_channel.send(embed=notify_embed)
       
       del self.active_votes[guild_id]

async def setup(bot):
   await bot.add_cog(CountingCog(bot))