# cogs/chatty_info.py

import discord
import time

from discord.ext import commands, Interaction

from utils.localization import translate
from utils.generic import handle_errors
from services.gemini import get_current_model
from utils.logger import bot_logger
from utils.context import get_context_prompt
from utils.config import BOT_START_TIME


class ChattyStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="chatty-info", description="Show info about the bot"
    )
    @handle_errors("chatty-info")
    async def chatty_info(self, interaction: Interaction):
        """
        Display bot info including uptime, active model, and version.
        """
        server_name = interaction.guild.name if interaction.guild else "DM"
        context_content = get_context_prompt(server_name)
        context_file = "Active" if context_content else "None"

        # Calculate uptime
        uptime_seconds = int(time.time() - BOT_START_TIME)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours >= 24:
            days, hours = divmod(hours, 24)
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
            uptime_str = f"{hours}h {minutes}m {seconds}s"

        message_text = translate(
            "info_message",
            model=get_current_model(),
            context=context_file,
            uptime=uptime_str,
        )

        # --- LOG Info Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Info requested by %s (ID: %s) in [%s] | Context: %s | Uptime: %s",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            context_file,
            uptime_str,
        )

        await interaction.response.send_message(message_text)


async def setup(bot):
    await bot.add_cog(ChattyStatus(bot))
