import discord
import time

from discord.ext import commands
from discord import app_commands
from typing import Optional

from services.gemini_service import get_gemini_response
from utils.localization import t
from utils.db_utils import log_to_sqlite
from utils.generic import read_file_content, handle_errors
from utils.logger import bot_logger, error_logger
from utils.context import get_context_prompt


class ChattyGemini(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty", description="Ask a question to Coffy (Gemini model)"
    )
    @app_commands.describe(
        prompt="Your question or request for Coffy",
        allegato="(Optional) Attachment to analyze",
    )
    @handle_errors("chatty")
    async def chatty(
        self,
        interaction: discord.Interaction,
        prompt: str,
        allegato: Optional[discord.Attachment] = None,
    ):
        await interaction.response.defer()

        attachment_texts = []
        if allegato:
            result = await read_file_content(allegato)
            if result.startswith("⚠️") or result.startswith("❌"):
                await interaction.followup.send(result)
                return
            attachment_texts.append(result)

        final_prompt = prompt
        if attachment_texts:
            final_prompt += (
                "\n\n" + t("attachment_content") + "\n" + "\n".join(attachment_texts)
            )

        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Prompt received from %s (ID: %s) in [%s]: %s",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            prompt[:100],
        )

        server_name = interaction.guild.name if interaction.guild else "DM"
        context_prompt = get_context_prompt(server_name)

        if context_prompt:
            full_prompt = context_prompt.strip() + "\n\n" + final_prompt
            bot_logger.info("Context applied for server '%s'", server_name)
        else:
            full_prompt = final_prompt

        response_text = get_gemini_response(full_prompt)

        if response_text is None:
            await interaction.followup.send(t("gemini_error"))
            return

        log_to_sqlite(
            interaction.user, interaction.channel, final_prompt, response_text
        )

        if len(response_text) <= 4096:
            embed = discord.Embed(
                title=t("response_title"),
                description=response_text,
                color=discord.Color.green(),
            )
            embed.set_footer(
                text=t("response_footer", user=interaction.user.display_name),
                icon_url=interaction.user.display_avatar.url,
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(response_text)


async def setup(bot):
    await bot.add_cog(ChattyGemini(bot))
