import discord
from discord.ext import commands
from discord import app_commands

from services.hugging_face import generate_image
from utils.localization import translate
from utils.generic import handle_errors, safe_delete
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
                translate("image_no_prompt"), ephemeral=True
            )
            return

        await interaction.response.defer()

        # --- LOG Prompt ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
        bot_logger.info(
            "Image prompt from %s (ID: %s) in [%s]: %s",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            preview,
        )

        image_file = await generate_image(prompt)

        if image_file == "loading":
            bot_logger.warning("Image model loading for: %s", preview)
            await interaction.followup.send(translate("image_loading"))
        elif image_file == "limit":
            bot_logger.warning("API rate limit for: %s", preview)
            await interaction.followup.send(translate("image_limit"))
        elif image_file:
            bot_logger.info(
                "Image generated successfully for %s", interaction.user.display_name
            )
            await interaction.followup.send(file=discord.File(image_file))
            safe_delete(image_file)
        else:
            error_logger.error("Image generation failed for: %s", preview)
            await interaction.followup.send(translate("image_error"))


async def setup(bot):
    await bot.add_cog(ChattyImage(bot))
