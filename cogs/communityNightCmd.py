import discord
import datetime
import time
import pytz
from discord import app_commands
from discord.ext import commands

def dateCalculator(nextday, chosenhour, chosenminutes, eveormorn):
    epoch = 00000
    timezone = pytz.timezone("Australia/Brisbane")
    today = datetime.datetime.now(timezone).date()

    # Get current date
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # We need to store weekday and convert user input
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    target_day_index = days_of_week.index(nextday.capitalize())

    # Lets find out how manydays until next occurrence of target day
    today_index = today.weekday()
    days_until_next =(target_day_index - today_index) % 7
    
    # If today is the target day, return today's 
    next_day_date = today if days_until_next == 0 else today + datetime.timedelta(days=days_until_next)

    # Extract the next occurrences date
    next_day = next_day_date.day
    next_month = next_day_date.month
    next_year = next_day_date.year

    if eveormorn.lower() == "pm" and chosenhour != 12:
        chosenhour += 12
    elif eveormorn.lower() == "am" and chosenhour == 12:
        chosenhour = 0
    
    dt = datetime.datetime(next_year, next_month, next_day, chosenhour, chosenminutes, tzinfo=timezone)

    #convert to epoch time
    epoch = int(time.mktime(dt.timetuple())) # Convert to unix timestamp
 
    return epoch

class commNightCMD(commands.Cog):
    global banditColor
    banditColor = 0x0a8888
    def __init__(self, bot):
        self.bot = bot
        
    # Error handling method for application commands
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You do NOT have the required role to use this command.", ephemeral=True)
        else:
            # Handle other errors
            if interaction.response.is_done():
                await interaction.followup.send(f"An error occurred: {str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            print(f"Error in command: {str(error)}")
            
    @app_commands.command(name="communitynight", description="Schedule a community night")
    @commands.has_any_role(1044403662996373613, 1044403662996373612)
    async def scheduler(self, interaction: discord.Interaction, gamename: str, nextday: str, choosehour: int, chooseminutes: int, amorpm: str):
        await interaction.response.send_message("Sure", ephemeral=True)
        #Schedule community night command here
        embed = discord.Embed(
            title="It's Community Night!!!",
            color=banditColor
        )
        epochtime = dateCalculator(nextday, choosehour, chooseminutes, amorpm)
        embed.add_field(name="Game 🎮", value=f'{gamename}', inline=True)
        embed.add_field(name="", value="Make sure your game is downloaded before hand!", inline=False)
        embed.add_field(name="Timestamp ⏲️", value=f'<t:{epochtime}:F> [TIMES CONVERTED]', inline=False)
        embed.set_footer(text=f'{interaction.user}', icon_url=f'{interaction.user.displayAvatarURL}')
        if self.bot.events_channel:
            await self.bot.events_channel.send("@everyone", embed=embed)
     

async def setup(bot):
    await bot.add_cog(commNightCMD(bot), guilds=[discord.Object(id=bot.guild_id)])