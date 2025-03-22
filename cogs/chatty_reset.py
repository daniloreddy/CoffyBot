import discord

from discord.ext import commands
from discord import app_commands

from utils.localization import t
from utils.memory import user_memory
from utils.generic import check_admin, handle_errors
from utils.logger import bot_logger


class ChattyMemory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-reset", description="Reset the chat memory with the bot"
    )
    @handle_errors("chatty-reset")
    async def chatty_reset(self, interaction: discord.Interaction):
        if not await check_admin(interaction):
            return

        user_id = interaction.user.id
        user_memory.pop(user_id, None)

        # --- LOG Memory Reset ---
        bot_logger.info(
            "Memory reset by user %s (ID: %s)", interaction.user.display_name, user_id
        )

        await interaction.response.send_message(t("memory_reset"), ephemeral=False)
        try:
            await interaction.channel.last_message.add_reaction("🧹")
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(ChattyMemory(bot))
