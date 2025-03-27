# cogs/chatty_tts.py

import discord

from discord.ext import commands
from discord import app_commands, Interaction

from utils.localization import translate
from utils.generic import handle_errors, safe_delete
from utils.logger import bot_logger, error_logger
from core.handler import process_tts


class ChattyTTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-tts", description="Generate audio from text (text-to-speech)"
    )
    @app_commands.describe(testo="Text to convert to audio")
    @handle_errors("chatty-tts")
    async def chatty_tts(self, interaction: Interaction, testo: str):
        """
        Generate a TTS audio response from the provided text.

        Args:
            interaction (Interaction): The command interaction.
            testo (str): Text to convert to audio.
        """
        if not testo.strip():
            await interaction.response.send_message(
                translate("tts_no_text"), ephemeral=True
            )
            return

        await interaction.response.defer()

        # --- LOG TTS Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        preview = testo[:50] + "..." if len(testo) > 50 else testo
        bot_logger.info(
            "TTS requested by %s (ID: %s) in [%s]: '%s'",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            preview,
        )

        audio_file = process_tts(testo)
        if audio_file:
            bot_logger.info(
                "TTS audio generated successfully for %s", interaction.user.display_name
            )
            await interaction.followup.send(file=discord.File(audio_file))
            safe_delete(audio_file)
        else:
            error_logger.error(
                "TTS generation failed for %s", interaction.user.display_name
            )
            await interaction.followup.send(translate("tts_error"))


async def setup(bot):
    await bot.add_cog(ChattyTTS(bot))
