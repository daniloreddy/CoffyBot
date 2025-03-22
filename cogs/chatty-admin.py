import discord
from discord.ext import commands
from discord import app_commands

from utils.localization import t
from utils.generic import handle_errors, check_admin
from services.gemini_service import change_model, SUPPORTED_MODELS
from utils.logger import bot_logger, error_logger
from utils.context import set_context_file, reset_context


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
            for mod in SUPPORTED_MODELS
            if current.lower() in mod.lower()
        ]
        return suggestions[:5]

    # --- CONTEXT SET ---
    @app_commands.command(
        name="chatty-context",
        description="Set the context file for this server",
    )
    @app_commands.describe(filename="Name of the file in prompts/ (without .txt)")
    @handle_errors("chatty-context")
    async def chatty_context(self, interaction: discord.Interaction, filename: str):
        if not await check_admin(interaction):
            return

        filename = filename.strip()
        if not filename:
            await interaction.response.send_message(
                t("invalid_context_file"), ephemeral=True
            )
            return

        if not filename.endswith(".txt"):
            filename += ".txt"

        server_name = (
            interaction.guild.name
            if interaction.guild
            else f"DM-{interaction.user.name}"
        )

        result = set_context_file(server_name, filename)

        if result:
            bot_logger.info(
                "Context set to '%s' by %s (ID: %s)",
                filename,
                interaction.user.display_name,
                interaction.user.id,
            )
            await interaction.response.send_message(
                t("context_set", file=filename), ephemeral=True
            )
        else:
            error_logger.warning(
                "Invalid context file attempt by %s (ID: %s): %s",
                interaction.user.display_name,
                interaction.user.id,
                filename,
            )
            await interaction.response.send_message(
                t("invalid_context_file"), ephemeral=True
            )

    # --- CONTEXT RESET ---
    @app_commands.command(
        name="chatty-context-reset",
        description="Reset the context file for this server",
    )
    @handle_errors("chatty-context-reset")
    async def chatty_context_reset(self, interaction: discord.Interaction):
        if not await check_admin(interaction):
            return

        server_name = (
            interaction.guild.name
            if interaction.guild
            else f"DM-{interaction.user.name}"
        )

        reset_context(server_name)
        bot_logger.info(
            "Context reset by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )
        await interaction.response.send_message(t("context_reset"), ephemeral=True)


async def setup(bot):
    await bot.add_cog(ChattyAdmin(bot))
