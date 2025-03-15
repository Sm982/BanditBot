import discord
from discord import app_commands, Color, SelectOption, TextStyle
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput
from logger import logger
from date_calculator import dateCalculator
import time

# Step 1 - Ask user if they'd like to ping everyone, here or no one - yes
# Step 2 - Ask what time (12am-11pm) - yes
# Step 3 - Ask what day (Monday-Sunday) - yes
# Step 4 - Ask in a modal what game they'd like to play
# Step 5 - Create an embed
# Step 6 - Buttons after the embed
# Step 7 - Add a role to the user after clicking button
# Step 8 - Event loop

class cmNightCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        
    global banditColor
    banditColor = 0x0a8888
    
    class MentionSelectView(View):
        def __init__(self, cog):
            super().__init__(timeout=60)
            self.cog = cog
            
            self.mention_select = Select(
                placeholder="Please select an option...",
                min_values=1,
                max_values=1,
                options=[
                    SelectOption(label="No mentions", description="We aren't tagging everyone", emoji="🔕", value="notag"),
                    SelectOption(label="@everyone", description="So you want to be annoying and ping everyone..", emoji="🔔", value="tageveryone"),
                    SelectOption(label="@here", description="So you still want to be annoying, but you'll only tag the online people... Got it..", emoji="🔔", value="taghere")
                ]
            )
            
            self.mention_select.callback = self.mention_selected
            self.add_item(self.mention_select)
            
        async def mention_selected(self, interaction: discord.Interaction):
            selected_mention = self.mention_select.values[0]
            await interaction.response.send_message(
                "You've selected who you want to annoy. Now decide what time.",
                view=cmNightCommand.TimeSelectView(self.cog, selected_mention)
            )
            
    class TimeSelectView(View):
        def __init__(self, cog, selected_mention):
            super().__init__(timeout=60)
            self.cog = cog
            self.selected_mention = selected_mention
            
            self.time_select = Select(
                placeholder="Please choose an option...",
                min_values=1,
                max_values=1,
                options=[
                    SelectOption(label="12:00am", description="Event starts at 12:00am Brisbane Time", emoji="🕒", value="12am"),
                    SelectOption(label="12:30am", description="Event starts at 12:30am Brisbane Time", emoji="🕒", value="1230am"),
                    SelectOption(label="1:00am", description="Event starts at 1:00am Brisbane Time", emoji="🕒", value="1am"),
                    SelectOption(label="1:30am", description="Event starts at 1:30am Brisbane Time", emoji="🕒", value="130am"),
                    SelectOption(label="2:00am", description="Event starts at 2:00am Brisbane Time", emoji="🕒", value="2am"),
                    SelectOption(label="2:30am", description="Event starts at 2:30am Brisbane Time", emoji="🕒", value="230am"),
                    SelectOption(label="3:00am", description="Event starts at 3:00am Brisbane Time", emoji="🕒", value="3am"),
                    SelectOption(label="3:30am", description="Event starts at 3:30am Brisbane Time", emoji="🕒", value="330am"),
                    SelectOption(label="4:00am", description="Event starts at 4:00am Brisbane Time", emoji="🕒", value="4am"),
                    SelectOption(label="4:30am", description="Event starts at 4:30am Brisbane Time", emoji="🕒", value="430am"),
                    SelectOption(label="5:00am", description="Event starts at 5:00am Brisbane Time", emoji="🕒", value="5am"),
                    SelectOption(label="5:30am", description="Event starts at 5:30am Brisbane Time", emoji="🕒", value="530am"),
                    SelectOption(label="6:00am", description="Event starts at 6:00am Brisbane Time", emoji="🕒", value="6am"),
                    SelectOption(label="6:30am", description="Event starts at 6:30am Brisbane Time", emoji="🕒", value="630am"),
                    SelectOption(label="7:00am", description="Event starts at 7:00am Brisbane Time", emoji="🕒", value="7am"),
                    SelectOption(label="7:30am", description="Event starts at 7:30am Brisbane Time", emoji="🕒", value="730am"),
                    SelectOption(label="8:00am", description="Event starts at 8:00am Brisbane Time", emoji="🕒", value="8am"),
                    SelectOption(label="8:30am", description="Event starts at 8:30am Brisbane Time", emoji="🕒", value="830am"),
                    SelectOption(label="9:00am", description="Event starts at 9:00am Brisbane Time", emoji="🕒", value="9am"),
                    SelectOption(label="9:30am", description="Event starts at 9:30am Brisbane Time", emoji="🕒", value="930am"),
                    SelectOption(label="10:00am", description="Event starts at 10:00am Brisbane Time", emoji="🕒", value="10am"),
                    SelectOption(label="10:30am", description="Event starts at 10:30am Brisbane Time", emoji="🕒", value="1030am"),
                    SelectOption(label="11:00am", description="Event starts at 11:00am Brisbane Time", emoji="🕒", value="11am"),
                    SelectOption(label="11:30am", description="Event starts at 11:30am Brisbane Time", emoji="🕒", value="1130am"),
                    SelectOption(label="12:00pm", description="Event starts at 12:00pm Brisbane Time", emoji="🕒", value="12pm"),
                    SelectOption(label="12:30pm", description="Event starts at 12:30pm Brisbane Time", emoji="🕒", value="1230pm"),
                    SelectOption(label="1:00pm", description="Event starts at 1:00pm Brisbane Time", emoji="🕒", value="1pm"),
                    SelectOption(label="1:30pm", description="Event starts at 1:30pm Brisbane Time", emoji="🕒", value="130pm"),
                    SelectOption(label="2:00pm", description="Event starts at 2:00pm Brisbane Time", emoji="🕒", value="2pm"),
                    SelectOption(label="2:30pm", description="Event starts at 2:30pm Brisbane Time", emoji="🕒", value="230pm"),
                    SelectOption(label="3:00pm", description="Event starts at 3:00pm Brisbane Time", emoji="🕒", value="3pm"),
                    SelectOption(label="3:30pm", description="Event starts at 3:30pm Brisbane Time", emoji="🕒", value="330pm"),
                    SelectOption(label="4:00pm", description="Event starts at 4:00pm Brisbane Time", emoji="🕒", value="4pm"),
                    SelectOption(label="4:30pm", description="Event starts at 4:30pm Brisbane Time", emoji="🕒", value="430pm"),
                    SelectOption(label="5:00pm", description="Event starts at 5:00pm Brisbane Time", emoji="🕒", value="5pm"),
                    SelectOption(label="5:30pm", description="Event starts at 5:30pm Brisbane Time", emoji="🕒", value="530pm"),
                    SelectOption(label="6:00pm", description="Event starts at 6:00pm Brisbane Time", emoji="🕒", value="6pm"),
                    SelectOption(label="6:30pm", description="Event starts at 6:30pm Brisbane Time", emoji="🕒", value="630pm"),
                    SelectOption(label="7:00pm", description="Event starts at 7:00pm Brisbane Time", emoji="🕒", value="7pm"),
                    SelectOption(label="7:30pm", description="Event starts at 7:30pm Brisbane Time", emoji="🕒", value="730pm"),
                    SelectOption(label="8:00pm", description="Event starts at 8:00pm Brisbane Time", emoji="🕒", value="8pm"),
                    SelectOption(label="8:30pm", description="Event starts at 8:30pm Brisbane Time", emoji="🕒", value="830pm"),
                    SelectOption(label="9:00pm", description="Event starts at 9:00pm Brisbane Time", emoji="🕒", value="9pm"),
                    SelectOption(label="9:30pm", description="Event starts at 9:30pm Brisbane Time", emoji="🕒", value="930pm"),
                    SelectOption(label="10:00pm", description="Event starts at 10:00pm Brisbane Time", emoji="🕒", value="10pm"),
                    SelectOption(label="10:30pm", description="Event starts at 10:30pm Brisbane Time", emoji="🕒", value="1030pm"),
                    SelectOption(label="11:00pm", description="Event starts at 11:00pm Brisbane Time", emoji="🕒", value="11pm"),
                    SelectOption(label="11:30pm", description="Event starts at 11:30pm Brisbane Time", emoji="🕒", value="1130pm")
                ]
            )
            
            self.time_select.callback = self.time_selected
            self.add_item(self.time_select)
            
        async def time_selected(self, interaction: discord.Interaction):
            selected_time = self.time_select.values[0]
            await interaction.response.send_message(
                "You've now selected a time. Now decide what day.",
                view=cmNightCommand.DaySelectView(self.cog, self.selected_mention, selected_time)
            )
            
    class DaySelectView(View):
        def __init__(self, cog, selected_mention, selected_time):
            super().__init__(timeout=60)
            self.cog = cog
            self.selected_mention = selected_mention
            self.selected_time = selected_time
            
            self.day_select = Select(
                placeholder="Please choose an option...",
                min_values=1,
                max_values=1,
                options=[
                    SelectOption(label="Monday", description="The event is going to take place on Monday", emoji="📅", value="monday"),
                    SelectOption(label="Tuesday", description="The event is going to take place on Tuesday", emoji="📅", value="tuesday"),
                    SelectOption(label="Wednesday", description="The event is going to take place on Wednesday", emoji="📅", value="wednesday"),
                    SelectOption(label="Thursday", description="The event is going to take place on Thursday", emoji="📅", value="thursday"),
                    SelectOption(label="Friday", description="The event is going to take place on Friday", emoji="📅", value="friday"),
                    SelectOption(label="Saturday", description="The event is going to take place on Saturday", emoji="📅", value="saturday"),
                    SelectOption(label="Sunday", description="The event is going to take place on Sunday", emoji="📅", value="sunday")
                ]
            )
            
            self.day_select.callback = self.day_selected
            self.add_item(self.day_select)
            
        async def day_selected(self, interaction: discord.Interaction):
            selected_day = self.day_select.values[0]

            await interaction.response.send_modal(
                cmNightCommand.cmModal(self.cog, self.selected_mention, self.selected_time, selected_day)
            )

    class cmModal(Modal):
        def __init__(self, cog, mention_type, time_type, day_type):
            super().__init__(title="What game are we playing?")
            self.cog = cog
            self.mention_type = mention_type
            self.time_type = time_type
            self.day_type = day_type

            self.game_input = TextInput(
                label="Game being played",
                placeholder="Enter a game for your community night",
                style=TextStyle.short,
                required=True,
                max_length=30
            )

            self.add_item(self.game_input)

        async def on_submit(self, interaction: discord.Interaction):
            game_name = self.game_input.value
            channel = interaction.client.get_channel(self.cog.bot.events_channel_id)

            if not channel:
                await interaction.response.send_message("Critical error, could not find the selected channel.", ephemeral=True)
                logger.error("Critical error, could not find the events channel for CM night command")
                return
            
            embed = discord.Embed(
                title="It's Community Night!!!",
                description="It's TheBanditWombat's weekly Community Night!",
                color=banditColor
            )
            
            
            epochtime = dateCalculator(self.day_type, self.time_type)
            
            embed.add_field(name="Game 🎮", value=game_name, inline=True)
            embed.add_field(name="", value="Make sure your game is downloaded before hand!", inline=False)
            embed.add_field(name="Timestamp ⏲️", value=f'<t:{epochtime}:F> [TIMES CONVERTED]', inline=True)
            embed.set_footer(text=f'{interaction.user.display_name}', icon_url=f'{interaction.user.display_avatar.url}')
            
            # Determine the mention string based on selected option
            mention_str = ""
            if self.mention_type == "tageveryone":
                mention_str = "@everyone"
            elif self.mention_type == "taghere":
                mention_str = "@here"
                
            await channel.send(mention_str, embed=embed)
            await interaction.response.send_message("Community night announcement has been posted!", ephemeral=True)
            logger.info(f'User {interaction.user.display_name} sent the command Community Night')

    @app_commands.command(name="cmnight", description="Create a community night announcement")
    async def cm_night(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Let's set up a community night! First, select who you'd like to notify.",
            view=self.MentionSelectView(self),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(cmNightCommand(bot), guilds=[discord.Object(id=bot.guild_id)])