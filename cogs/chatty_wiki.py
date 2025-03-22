import discord

from discord.ext import commands
from discord import app_commands

from services.wikipedia_service import search_wikipedia
from utils.generic import handle_errors
from utils.logger import bot_logger


class ChattyWiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-wiki", description="Search for a term on Wikipedia"
    )
    @app_commands.describe(termine="Term to search on Wikipedia")
    @handle_errors("chatty-wiki")
    async def chatty_wiki(self, interaction: discord.Interaction, termine: str):
        await interaction.response.defer()

        # --- Log Wikipedia Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Wikipedia search by %s (ID: %s) in [%s]: term='%s'",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            termine,
        )

        title, description, link, image = search_wikipedia(termine)

        embed = discord.Embed(
            title=f"📚 Wikipedia: {title}",
            description=description,
            color=discord.Color.gold(),
        )
        if link:
            embed.add_field(name="🔗 Link", value=link, inline=False)
        if image:
            embed.set_thumbnail(url=image)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ChattyWiki(bot))
