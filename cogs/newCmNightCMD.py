import discord
from discord import app_commands, Color, SelectOption, TextStyle
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput
from logger import logger
import time

# Step 1 - Ask user if they'd like to ping everyone, here or no one
# Step 2 - Ask what time (12am-11pm)
# Step 3 - Ask what day (Monday-Sunday)
# Step 4 - Ask in a modal what game they'd like to play
# Step 5 - Create an embed
# Step 6 - Buttons after the embed
# Step 7 - Add a role to the user after clicking button
# Step 8 - Event loop

class cmNightCommand(commands.cog):
    def __init(self, bot):
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
                view=cmNightCommand.TimeSelectView(self.cog, self.selected_mention)
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
            time_selected = self.time_select.values[0]
            await interaction.response.send_message(
                "You've now selected a time. Now decide what day.",
                view=cmNightCommand.DaySelectView(self.cog, self.selected_mention, self.time_selected)
            )
            
    class DaySelectView(View):
        def __init__(self, cog):
            super().__init__(timeout=60)
            self.cog = cog
            self.selected_mention = selected_mention
            self.time_selected = time_selected
            
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
            
        async def day_selected(self, interaction: discord.Interaction)