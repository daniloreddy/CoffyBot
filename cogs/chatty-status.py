import discord
import os
import time

from discord.ext import commands

from utils.localization import t
from utils.memory import user_memory, MEMORY_FILE
from utils.generic import handle_errors
from services.gemini_service import MODEL
from utils.logger import bot_logger
from utils.context import server_context
from bot import BOT_START_TIME


class ChattyStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="chatty-info", description="Show info about the bot and memory"
    )
    @handle_errors("chatty-info")
    async def chatty_info(self, interaction: discord.Interaction):
        users_memorized = len(user_memory)
        server_name = interaction.guild.name if interaction.guild else "DM"

        context_file = server_context.get(server_name, "None")

        # Calculate memory.json size
        memory_size = 0
        try:
            memory_size = os.path.getsize(MEMORY_FILE)
        except FileNotFoundError:
            memory_size = 0

        if memory_size < 1024:
            size_str = f"{memory_size} B"
        elif memory_size < 1024 * 1024:
            size_str = f"{memory_size / 1024:.2f} KB"
        else:
            size_str = f"{memory_size / (1024 * 1024):.2f} MB"

        # Calculate uptime
        uptime_seconds = int(time.time() - BOT_START_TIME)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours >= 24:
            days, hours = divmod(hours, 24)
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
            uptime_str = f"{hours}h {minutes}m {seconds}s"

        message_text = t(
            "info_message",
            model=MODEL,
            users=users_memorized,
            context=context_file,
            memsize=size_str,
            uptime=uptime_str
        )

        # --- LOG Info Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Info requested by %s (ID: %s) in [%s] | Context: %s | MemSize: %s | Uptime: %s",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            context_file,
            size_str,
            uptime_str,
        )

        await interaction.response.send_message(message_text)


async def setup(bot):
    await bot.add_cog(ChattyStatus(bot))
