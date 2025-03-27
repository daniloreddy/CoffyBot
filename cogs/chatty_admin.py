# cogs/chatty_admin.py

import discord
import os
import sqlite3

from discord.ext import commands
from discord import app_commands

from utils.localization import translate
from utils.generic import (
    handle_errors,
    require_discord_dm,
    require_discord_admin,
)
from services.gemini import (
    change_model,
    get_supported_models,
    get_current_model,
)
from utils.logger import bot_logger, error_logger
from utils.context import set_context_file, reset_context, get_server_context
from utils.config import DB_FILE


class ChattyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-admin-model",
        description="Change the Gemini model used by the bot (ADMIN+DM only)",
    )
    @app_commands.describe(modello="Name of the new model (e.g., gemini-1.5-flash)")
    @handle_errors("chatty-admin-model")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_model(self, interaction: discord.Interaction, modello: str):

        ok = change_model(modello)
        if ok:
            bot_logger.info(
                "Gemini model switched by %s (ID: %s) to: %s",
                interaction.user.display_name,
                interaction.user.id,
                modello,
            )
            await interaction.response.send_message(
                translate("model_switched", model=modello)
            )
        else:
            error_logger.warning(
                "Invalid model switch attempt by %s (ID: %s): %s",
                interaction.user.display_name,
                interaction.user.id,
                modello,
            )
            await interaction.response.send_message(translate("invalid_model"))

    @chatty_model.autocomplete("modello")
    async def autocomplete_models(self, interaction: discord.Interaction, current: str):
        suggestions = [
            app_commands.Choice(name=mod, value=mod)
            for mod in get_supported_models()
            if current.lower() in mod.lower()
        ]
        return suggestions[:5]

    # --- CONTEXT SET ---
    @app_commands.command(
        name="chatty-admin-context",
        description="Set the context file for this server (ADMIN only)",
    )
    @app_commands.describe(filename="Name of the file in prompts/ (without .txt)")
    @handle_errors("chatty-admin-context")
    @require_discord_admin()
    async def chatty_context(self, interaction: discord.Interaction, filename: str):

        filename = filename.strip()
        if not filename:
            await interaction.response.send_message(
                translate("invalid_context_file"), ephemeral=True
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
                translate("context_set"), ephemeral=True
            )
        else:
            error_logger.warning(
                "Invalid context file attempt by %s (ID: %s): %s",
                interaction.user.display_name,
                interaction.user.id,
                filename,
            )
            await interaction.response.send_message(
                translate("invalid_context_file"), ephemeral=True
            )

    # --- CONTEXT RESET ---
    @app_commands.command(
        name="chatty-admin-context-reset",
        description="Reset the context file for this server (ADMIN only)",
    )
    @handle_errors("chatty-admin-context-reset")
    @require_discord_admin()
    async def chatty_context_reset(self, interaction: discord.Interaction):
        """
        Reset the context prompt for the current server.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
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
        await interaction.response.send_message(
            translate("context_reset"), ephemeral=True
        )

    @app_commands.command(
        name="chatty-admin-stats",
        description="\ud83d\udcca Show bot statistics  (ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-stats")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_stats(self, interaction: discord.Interaction):
        """
        Show basic bot usage statistics including number of conversations and unique users.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
        server_context_info = (
            "\n".join([f"{srv}: {file}" for srv, file in get_server_context.items()])
            or "None"
        )

        embed = discord.Embed(
            title=translate("embed_stats_title"),
            description=translate("embed_stats_desc", model=get_current_model()),
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=translate("embed_context_title"),
            value=server_context_info,
            inline=False,
        )
        await interaction.response.send_message(embed=embed)
        bot_logger.info(
            "Bot stats requested via DM by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )

    @app_commands.command(
        name="chatty-admin-activity",
        description="\ud83d\udcc5 Show daily message activity (last 7 days, ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-activity")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_activity(self, interaction: discord.Interaction):
        """
        Show daily conversation activity over the last 7 days in graphical format.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
        if not os.path.isfile(DB_FILE):
            await interaction.response.send_message(
                translate("db_missing_dm"), ephemeral=True
            )
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DATE(timestamp), COUNT(*) FROM conversations GROUP BY DATE(timestamp) ORDER BY DATE(timestamp) DESC LIMIT 7"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message(
                translate("no_activity_dm"), ephemeral=True
            )
            return

        activity_log = "\n".join([f"{day}: {count} messages" for day, count in rows])
        embed = discord.Embed(
            title=translate("embed_activity_title"),
            description=activity_log,
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)
        bot_logger.info(
            "Activity report requested via DM by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )

    @app_commands.command(
        name="chatty-admin-lastlogs",
        description="\ud83d\udcd2\ufe0f Show last 10 conversations (ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-lastlogs")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_lastlogs(self, interaction: discord.Interaction):
        """
        Show the last 10 Gemini prompts and responses for moderation or debugging.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
        if not os.path.isfile(DB_FILE):
            await interaction.response.send_message(
                translate("db_missing_dm"), ephemeral=True
            )
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, user, user_id, channel, message, response FROM conversations ORDER BY id DESC LIMIT 10"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message(
                translate("no_conversations_dm"), ephemeral=True
            )
            return

        logs = ""
        for row in rows:
            logs += f"\ud83d\udd52 {row[0]} - \ud83d\udc64 {row[1]} ({row[2]}) - \ud83d\udce2 #{row[3]}\n\ud83d\udcac {row[4]}\n\ud83e\udd16 {row[5]}\n{'-'*40}\n"

        output_text = translate("last_conversations", logs=logs)
        if len(output_text) <= 2000:
            await interaction.response.send_message(output_text)
        else:
            temp_file_name = "last_conversations.txt"
            with open(temp_file_name, "w", encoding="utf-8", errors="ignore") as fp:
                fp.write(output_text)

            await interaction.response.send_message(
                "🗂️ Last 10 Conversations (file attached):",
                file=discord.File(temp_file_name),
            )
            os.remove(temp_file_name)

        bot_logger.info(
            "Last logs requested via DM by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )

    @app_commands.command(
        name="chatty-admin-help",
        description="\ud83d\udcd6 Show admin commands (ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-help")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_help_admin(self, interaction: discord.Interaction):
        """
        Display a list of all available admin commands and their descriptions.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
        await interaction.response.send_message(
            translate("admin_help_message_discord"), ephemeral=True
        )
        bot_logger.info(
            "Admin help requested via DM by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )

    @app_commands.command(
        name="chatty-admin-models",
        description="List all supported Gemini models (ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-models")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_admin_models(self, interaction: discord.Interaction):
        """
        List all available Gemini models and highlight the currently active one.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
        current = get_current_model()
        model_list = "\n".join(
            [
                f"🔹 {m} {'(active)' if m == current else ''}".strip()
                for m in get_supported_models()
            ]
        )
        await interaction.response.send_message(
            translate("available_models", models=model_list), ephemeral=True
        )
        bot_logger.info(
            "Model list requested via DM by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )

    @app_commands.command(
        name="chatty-admin-contexts",
        description="List all available context files (ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-contexts")
    @require_discord_dm()
    @require_discord_admin()
    async def chatty_admin_contexts(self, interaction: discord.Interaction):
        """
        List all available context files in the prompts/ directory.

        Args:
            interaction (discord.Interaction): The command interaction.
        """
        try:
            files = [f for f in os.listdir("prompts") if f.endswith(".txt")]
            file_list = "\n".join(files) if files else translate("no_context_files")
            await interaction.response.send_message(
                translate("available_context_files", files=file_list), ephemeral=True
            )
            bot_logger.info(
                "Context files listed via DM by %s (ID: %s)",
                interaction.user.display_name,
                interaction.user.id,
            )
        except Exception as e:
            error_logger.error("Failed to list context files: %s", str(e))
            await interaction.response.send_message(
                translate("context_files_error"), ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ChattyAdmin(bot))
