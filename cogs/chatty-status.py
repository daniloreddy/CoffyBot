import discord

from discord.ext import commands

from utils.localization import t
from utils.memory import user_memory
from utils.generic import handle_errors
from services.gemini_service import MODEL
from utils.logger import bot_logger  # Add logger


class ChattyStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="chatty-info", description="Show info about the bot and memory"
    )
    @handle_errors("chatty-info")
    async def chatty_info(self, interaction: discord.Interaction):
        users_memorized = len(user_memory)
        message_text = t("info_message", model=MODEL, users=users_memorized)

        # --- LOG Info Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Info requested by %s (ID: %s) in [%s]",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
        )

        await interaction.response.send_message(message_text)


async def setup(bot):
    await bot.add_cog(ChattyStatus(bot))
