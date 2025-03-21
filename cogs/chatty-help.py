import discord

from discord.ext import commands
from utils.localization import t


class ChattyHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="chatty-help", description="Show the list of available commands"
    )
    async def chatty_help(self, interaction: discord.Interaction):
        message_text = t("help_message")
        await interaction.response.send_message(message_text, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ChattyHelp(bot))
