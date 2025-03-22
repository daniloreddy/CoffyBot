import os
import discord

from discord.ext import commands
from discord import app_commands

from services.hugging_face_service import generate_image
from utils.localization import t
from utils.generic import handle_errors
from utils.logger import bot_logger, error_logger


class ChattyImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-image", description="Generate an image from a prompt"
    )
    @app_commands.describe(prompt="Description of the image to generate")
    @handle_errors("chatty-image")
    async def chatty_image(self, interaction: discord.Interaction, prompt: str):
        if not prompt.strip():
            await interaction.response.send_message(
                t("image_no_prompt"), ephemeral=True
            )
            return

        await interaction.response.defer()

        # --- LOG Prompt ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Image prompt received from %s (ID: %s) in [%s]: %s",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            prompt[:100],
        )

        image_file = generate_image(prompt)

        if image_file == "loading":
            bot_logger.warning(
                "Image model loading – prompt from %s: %s",
                interaction.user.display_name,
                prompt[:50],
            )
            await interaction.followup.send(t("image_loading"))
        elif image_file == "limit":
            bot_logger.warning(
                "API rate limit reached – prompt from %s: %s",
                interaction.user.display_name,
                prompt[:50],
            )
            await interaction.followup.send(t("image_limit"))
        elif image_file:
            bot_logger.info(
                "Image generated successfully for %s", interaction.user.display_name
            )
            await interaction.followup.send(file=discord.File(image_file))
            os.remove(image_file)
        else:
            error_logger.error("Image generation failed for prompt: %s", prompt[:50])
            await interaction.followup.send(t("image_error"))


async def setup(bot):
    await bot.add_cog(ChattyImage(bot))
