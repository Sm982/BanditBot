import discord
import datetime
import time
import pytz
from logger import logger
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

class watchPartCmd(commands.Cog):
    global banditColor
    banditColor = 0x0a8888
    def __init__(self, bot):
        self.bot = bot
        
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
            
    @app_commands.command(name="watchparty", description="Schedule a watch party night")
    @commands.has_any_role("Bandits Admins")
    async def scheduler(self, interaction: discord.Interaction, description: str, gamename: str, nextday: str, choosehour: int, chooseminutes: int, amorpm: str):
        errors = []

        if choosehour < 1 or choosehour > 12:
            errors.append("Hour must be between 1 and 12.")

        if chooseminutes < 0 or chooseminutes > 59:
            errors.append("Minutes must be between 0 and 59")
        
        amorpm = amorpm.lower()

        if amorpm not in ['am', 'pm']:
            errors.append("Time period must be either 'am' or 'pm'")
        
        if nextday.lower() not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            errors.append(f"Chosen day must be a valid day. Check for either spelling mistakes or choose a proper day. Your input: {nextday}")
        
        if errors:
            error_message = "❌ Invalid Input:\n" + "\n".join(f'{error}' for error in errors)
            logger.info(f'User {interaction.user.display_name} attempted the Community Night Command however the following errors were presented' + " - ".join(f'{error}' for error in errors))
            await interaction.response.send_message(error_message, ephemeral=True)
            return
        
        await interaction.response.send_message(f"Sending Message to {self.bot.events_channel.name}", ephemeral=True)
        #Schedule community night command here
        embed = discord.Embed(
            title="It's a Watch Party!",
            description=f"{description}",
            color=banditColor
        )
        epochtime = dateCalculator(nextday, choosehour, chooseminutes, amorpm)
        embed.add_field(name="What are we watching 📺", value=f'{gamename}', inline=True)
        embed.add_field(name="Timestamp ⏲️", value=f'<t:{epochtime}:F> [TIMES CONVERTED]', inline=False)
        embed.set_footer(text=f'{interaction.user.display_name}', icon_url=f'{interaction.user.display_avatar.url}')
        if self.bot.events_channel:
            await self.bot.events_channel.send(embed=embed)
            logger.info(f'User {interaction.user.display_name} sent the command Watch Party to the events channel. Custom user content was {description} and {gamename}')
     

async def setup(bot):
    await bot.add_cog(watchPartCmd(bot), guilds=[discord.Object(id=bot.guild_id)])