import discord
import re
from logger import logger
from discord import app_commands
from discord.ext import commands

class CountingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_count = 0
        self.last_user_id = None
        self.highest_count = 0

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
            await self.reset_count(message.channel, f"Wrong number! Expected {expected_number}, got {number}")
            await message.delete()
            return
        
        if message.author.id == self.last_user_id:
            await self.reset_count(message.channel, f"{message.author.mention} posted twic in a row!")
            await message.delete()
            return
        
        self.current_count = number
        self.last_user_id = message.author.id

        if number > self.highest_count:
            self.highest_count = number
        
        await message.add_reaction("✅")

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
async def setup(bot):
    await bot.add_cog(CountingCog(bot))