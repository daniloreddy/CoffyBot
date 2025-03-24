import discord
import os
import sqlite3

from discord.ext import commands
from discord import app_commands

from utils.localization import t
from utils.generic import handle_errors, check_admin, is_dm_only
from services.gemini import (
    change_model,
    get_supported_models,
    get_current_model,
)
from utils.logger import bot_logger, error_logger
from utils.context import set_context_file, reset_context, get_server_context
from utils.config import DB_FILE


# --- Helper Functions ---
async def check_admin_and_dm(interaction):
    if not await check_admin(interaction):
        return False
    if not is_dm_only(interaction):
        return False
    return True


class ChattyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-admin-model",
        description="Change the Gemini model used by the bot (ADMIN+DM only)",
    )
    @app_commands.describe(modello="Name of the new model (e.g., gemini-1.5-flash)")
    @handle_errors("chatty-admin-model")
    async def chatty_model(self, interaction: discord.Interaction, modello: str):
        if not await check_admin_and_dm(interaction):
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
            await interaction.response.send_message(t("context_set"), ephemeral=True)
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
        name="chatty-admin-context-reset",
        description="Reset the context file for this server (ADMIN only)",
    )
    @handle_errors("chatty-admin-context-reset")
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

    @app_commands.command(
        name="chatty-admin-stats",
        description="\ud83d\udcca Show bot statistics  (ADMIN+DM only)",
    )
    @handle_errors("chatty-admin-stats")
    async def chatty_stats(self, interaction: discord.Interaction):
        if not await check_admin_and_dm(interaction):
            return

        server_context_info = (
            "\n".join([f"{srv}: {file}" for srv, file in get_server_context.items()])
            or "None"
        )

        embed = discord.Embed(
            title=t("embed_stats_title"),
            description=t("embed_stats_desc", model=get_current_model()),
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=t("embed_context_title"), value=server_context_info, inline=False
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
    async def chatty_activity(self, interaction: discord.Interaction):
        if not await check_admin_and_dm(interaction):
            return

        if not os.path.isfile(DB_FILE):
            await interaction.response.send_message(t("db_missing_dm"), ephemeral=True)
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DATE(timestamp), COUNT(*) FROM conversations GROUP BY DATE(timestamp) ORDER BY DATE(timestamp) DESC LIMIT 7"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message(t("no_activity_dm"), ephemeral=True)
            return

        activity_log = "\n".join([f"{day}: {count} messages" for day, count in rows])
        embed = discord.Embed(
            title=t("embed_activity_title"),
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
    async def chatty_lastlogs(self, interaction: discord.Interaction):
        if not await check_admin_and_dm(interaction):
            return

        if not os.path.isfile(DB_FILE):
            await interaction.response.send_message(t("db_missing_dm"), ephemeral=True)
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
                t("no_conversations_dm"), ephemeral=True
            )
            return

        logs = ""
        for row in rows:
            logs += f"\ud83d\udd52 {row[0]} - \ud83d\udc64 {row[1]} ({row[2]}) - \ud83d\udce2 #{row[3]}\n\ud83d\udcac {row[4]}\n\ud83e\udd16 {row[5]}\n{'-'*40}\n"

        output_text = t("last_conversations", logs=logs)
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
    async def chatty_help_admin(self, interaction: discord.Interaction):
        if not await check_admin_and_dm(interaction):
            return

        await interaction.response.send_message(t("admin_help_message"), ephemeral=True)
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
    async def chatty_admin_models(self, interaction: discord.Interaction):
        if not await check_admin_and_dm(interaction):
            return

        current = get_current_model()
        model_list = "\n".join(
            [
                f"🔹 {m} {'(active)' if m == current else ''}".strip()
                for m in get_supported_models()
            ]
        )
        await interaction.response.send_message(
            t("available_models", models=model_list), ephemeral=True
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
    async def chatty_admin_contexts(self, interaction: discord.Interaction):
        if not await check_admin_and_dm(interaction):
            return

        try:
            files = [f for f in os.listdir("prompts") if f.endswith(".txt")]
            file_list = "\n".join(files) if files else t("no_context_files")
            await interaction.response.send_message(
                t("available_context_files", files=file_list), ephemeral=True
            )
            bot_logger.info(
                "Context files listed via DM by %s (ID: %s)",
                interaction.user.display_name,
                interaction.user.id,
            )
        except Exception as e:
            error_logger.error("Failed to list context files: %s", str(e))
            await interaction.response.send_message(
                t("context_files_error"), ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ChattyAdmin(bot))
