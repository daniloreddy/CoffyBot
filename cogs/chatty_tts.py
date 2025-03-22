import os
import discord

from discord.ext import commands
from discord import app_commands

from services.google_tts_service import generate_tts_audio
from utils.localization import t
from utils.generic import handle_errors
from utils.logger import bot_logger, error_logger


class ChattyTTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-tts", description="Generate audio from text (text-to-speech)"
    )
    @app_commands.describe(testo="Text to convert to audio")
    @handle_errors("chatty-tts")
    async def chatty_tts(self, interaction: discord.Interaction, testo: str):
        if not testo.strip():
            await interaction.response.send_message(t("tts_no_text"), ephemeral=True)
            return

        await interaction.response.defer()

        # --- LOG TTS Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "TTS requested by %s (ID: %s) in [%s]: '%s'",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            testo[:100],
        )

        audio_file = generate_tts_audio(testo)
        if audio_file:
            bot_logger.info(
                "TTS audio generated successfully for %s", interaction.user.display_name
            )
            await interaction.followup.send(file=discord.File(audio_file))
            os.remove(audio_file)
        else:
            error_logger.error(
                "TTS generation failed for %s", interaction.user.display_name
            )
            await interaction.followup.send(t("tts_error"))


async def setup(bot):
    await bot.add_cog(ChattyTTS(bot))
