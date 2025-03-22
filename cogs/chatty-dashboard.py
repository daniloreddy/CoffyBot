import discord
import os
import sqlite3

from discord.ext import commands
from discord import app_commands

from utils.localization import t
from utils.memory import user_memory, MEMORY_FILE
from utils.context import server_context
from services.gemini_service import MODEL
from utils.logger import bot_logger
from utils.generic import check_admin, handle_errors

DB_FILE = "chatty.db"

class BotAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_dm(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is None

    @app_commands.command(
        name="chatty-stats", description="\ud83d\udcca Show bot statistics (DM only)"
    )
    @handle_errors("chatty-stats")
    async def chatty_stats(self, interaction: discord.Interaction):
        if not self.is_dm(interaction):
            await interaction.response.send_message(
                t("dm_only_command"), ephemeral=True
            )
            return

        if not await check_admin(interaction):
            return

        users_memorized = len(user_memory)
        memory_size = (
            os.path.getsize(MEMORY_FILE) if os.path.isfile(MEMORY_FILE) else 0
        )
        memsize_str = (
            f"{memory_size / 1024:.2f} KB"
            if memory_size < 1024 * 1024
            else f"{memory_size / (1024 * 1024):.2f} MB"
        )

        server_context_info = (
            "\n".join([f"{srv}: {file}" for srv, file in server_context.items()])
            or "None"
        )

        embed = discord.Embed(
            title=t("embed_stats_title"),
            description=t(
                "embed_stats_desc",
                model=MODEL,
                users=users_memorized,
                memsize=memsize_str,
            ),
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
        name="chatty-activity",
        description="\ud83d\udcc5 Show daily message activity (last 7 days, DM only)",
    )
    @handle_errors("chatty-activity")
    async def chatty_activity(self, interaction: discord.Interaction):
        if not self.is_dm(interaction):
            await interaction.response.send_message(
                t("dm_only_command"), ephemeral=True
            )
            return

        if not await check_admin(interaction):
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
        name="chatty-lastlogs",
        description="\ud83d\udcd2\ufe0f Show last 10 conversations (DM only)",
    )
    @handle_errors("chatty-lastlogs")
    async def chatty_lastlogs(self, interaction: discord.Interaction):
        if not self.is_dm(interaction):
            await interaction.response.send_message(
                t("dm_only_command"), ephemeral=True
            )
            return

        if not await check_admin(interaction):
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
        name="chatty-help-admin",
        description="\ud83d\udcd6 Show admin commands (DM only)",
    )
    async def chatty_help_admin(self, interaction: discord.Interaction):
        if not self.is_dm(interaction):
            await interaction.response.send_message(
                t("dm_only_command"), ephemeral=True
            )
            return

        if not await check_admin(interaction):
            return

        await interaction.response.send_message(t("admin_help_message"), ephemeral=True)
        bot_logger.info(
            "Admin help requested via DM by %s (ID: %s)",
            interaction.user.display_name,
            interaction.user.id,
        )


async def setup(bot):
    await bot.add_cog(BotAdmin(bot))
