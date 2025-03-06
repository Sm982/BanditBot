# import discord
# from discord import app_commands
# from discord.ext import commands
# import datetime
# import time
# import pytz

# class ScheduleModal(discord.ui.Modal, title="Create Weekly Schedule"):
#     def __init__(self):
#         super().__init__()
        
#         # Create input fields for each day
#         days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
#         for day in days:
#             self.add_item(
#                 discord.ui.TextInput(
#                     label=f"{day} Schedule",
#                     placeholder="5:00PM-8:00PM (leave blank if not streaming)",
#                     required=False,
#                     style=discord.TextStyle.short
#                 )
#             )
            
#         self.add_item(
#             discord.ui.TextInput(
#                 label="Schedule Title",
#                 placeholder="This Week's Twitch Schedule",
#                 required=True,
#                 style=discord.TextStyle.short
#             )
#         )
    
#     async def on_submit(self, interaction: discord.Interaction):
#         # Get values from form
#         days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#         schedule_data = {}
        
#         for i, day in enumerate(days):
#             time_range = self.children[i].value.strip()
#             if time_range:
#                 schedule_data[day] = time_range
        
#         title = self.children[7].value
        
#         # Create embed
#         embed = await self.create_schedule_embed(title, schedule_data)
        
#         # Ask which channel to post to
#         await interaction.response.send_message(
#             "Schedule created! Choose where to post it:",
#             view=ChannelSelectView(embed),
#             ephemeral=True
#         )
    
#     async def on_error(self, interaction: discord.Interaction, error):
#         await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
    
#     async def create_schedule_embed(self, title, schedule_data):
#         embed = discord.Embed(
#             title=title,
#             description="Join us live on Twitch this week!",
#             color=0x0a8888  # Using banditColor
#         )
        
#         for day, time_range in schedule_data.items():
#             if time_range:
#                 # Parse time range and convert to timestamps if needed
#                 try:
#                     start_time, end_time = time_range.split("-")
#                     start_time = start_time.strip()
#                     end_time = end_time.strip()
                    
#                     # Convert to Discord timestamps
#                     start_timestamp = self.time_to_timestamp(day, start_time)
#                     end_timestamp = self.time_to_timestamp(day, end_time)
                    
#                     embed.add_field(
#                         name=day,
#                         value=f"🔴 **LIVE**: {start_timestamp} - {end_timestamp}",
#                         inline=False
#                     )
#                 except:
#                     # If parsing fails, just use the raw string
#                     embed.add_field(
#                         name=day, 
#                         value=f"🔴 **LIVE**: {time_range}", 
#                         inline=False
#                     )
#             else:
#                 embed.add_field(name=day, value="No stream scheduled", inline=False)
        
#         embed.set_footer(text="All times are in Eastern Time (ET)")
#         embed.set_thumbnail(url="https://brand.twitch.tv/assets/images/black.png")
        
#         return embed
    
#     def time_to_timestamp(self, day_str, time_str):
#         # Get the date for the next occurrence of this day
#         day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, 
#                    "Friday": 4, "Saturday": 5, "Sunday": 6}
        
#         today = datetime.datetime.now()
#         days_ahead = (day_map[day_str] - today.weekday()) % 7
#         next_day = today + datetime.timedelta(days=days_ahead)
        
#         # Parse the time
#         try:
#             time_obj = datetime.datetime.strptime(time_str, "%I:%M%p")
#         except ValueError:
#             try:
#                 time_obj = datetime.datetime.strptime(time_str, "%I:%M %p")
#             except ValueError:
#                 # If all parsing fails, return the original string
#                 return time_str
        
#         # Combine date and time
#         full_datetime = next_day.replace(
#             hour=time_obj.hour, 
#             minute=time_obj.minute,
#             second=0
#         )
        
#         # Apply timezone (assuming ET)
#         eastern = pytz.timezone('US/Eastern')
#         full_datetime = eastern.localize(full_datetime)
        
#         # Convert to Unix timestamp
#         timestamp = int(full_datetime.timestamp())
        
#         return f"<t:{timestamp}:t>"  # Short time format

# class ChannelSelectView(discord.ui.View):
#     def __init__(self, embed):
#         super().__init__()
#         self.embed = embed
        
#     @discord.ui.channel_select(
#         placeholder="Select a channel",
#         min_values=1, 
#         max_values=1,
#         channel_types=[discord.ChannelType.text]
#     )
#     async def channel_select(self, select, interaction):
#         channel = select.values[0]
#         await channel.send(embed=self.embed)
#         await interaction.response.send_message(f"Schedule posted in {channel.mention}!", ephemeral=True)

# class scheduleStreamCMD(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.banditColor = 0x0a8888

#     # Error handling method for slash commands
#     async def cog_app_command_error(self, interaction: discord.Interaction, error):
#         if isinstance(error, app_commands.errors.MissingAnyRole):
#             await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
#         else:
#             if interaction.response.is_done():
#                 await interaction.followup.send(f"An error occurred: {str(error)}", ephemeral=True)
#             else:
#                 await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
#             print(f"Error in command: {str(error)}")

#     @app_commands.command(name="schedulestreams", description="Schedule Bandit's streams for the week")
#     @app_commands.checks.has_any_role("Bandits Admins")
#     async def schedulestream(self, interaction: discord.Interaction):
#         modal = ScheduleModal()
#         await interaction.response.send_modal(modal)

# async def setup(bot):
#     await bot.add_cog(scheduleStreamCMD(bot), guilds=[discord.Object(id=bot.guild_id)])