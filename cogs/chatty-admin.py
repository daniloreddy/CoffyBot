import discord

from discord.ext import commands
from discord import app_commands

from utils.localization import t
from utils.generic import handle_errors, check_admin
from services.gemini_service import change_model
from utils.logger import bot_logger, error_logger  # Add loggers

AVAILABLE_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro"]


class ChattyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-model", description="Change the Gemini model used by the bot"
    )
    @app_commands.describe(modello="Name of the new model (e.g., gemini-1.5-flash)")
    @handle_errors("chatty-model")
    async def chatty_model(self, interaction: discord.Interaction, modello: str):
        if not await check_admin(interaction):
            return
        ok = change_model(modello)

        if ok:
            bot_logger.info(
                "Gemini model switched by %s (ID: %s) to: %s",
                interaction.user.display_name,
                interaction.user.id,
                modello,
            )
            await interaction.response.send_message(t("model_switched", model=modello))
        else:
            error_logger.warning(
                "Invalid model switch attempt by %s (ID: %s): %s",
                interaction.user.display_name,
                interaction.user.id,
                modello,
            )
            await interaction.response.send_message(t("invalid_model"))

    @chatty_model.autocomplete("modello")
    async def autocomplete_models(self, interaction: discord.Interaction, current: str):
        suggestions = [
            app_commands.Choice(name=mod, value=mod)
            for mod in AVAILABLE_MODELS
            if current.lower() in mod.lower()
        ]
        return suggestions[:5]


async def setup(bot):
    await bot.add_cog(ChattyAdmin(bot))
