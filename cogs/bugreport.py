import discord
from discord import app_commands, Color, SelectOption, TextStyle
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput
from logger import logger

# User inputs command /bugreport , opens modal with title and description, title and description gets sent to user sillymonkey982 ( CREATOR_USER_ID )
