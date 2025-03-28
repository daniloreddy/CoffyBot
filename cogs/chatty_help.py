# cogs/chatty_help.py

import discord

from discord import Interaction
from discord.ext import commands
from utils.localization import translate


class ChattyHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="chatty-help", description="Show the list of available commands"
    )
    async def chatty_help(self, interaction):
        """
        Display the list of available bot commands and descriptions.
        """
        message_text = translate("help_message_discord")
        await interaction.response.send_message(message_text, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ChattyHelp(bot))
