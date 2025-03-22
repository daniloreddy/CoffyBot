import discord

from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional

from services.weather_service import get_weather
from utils.localization import t
from utils.generic import handle_errors
from utils.logger import bot_logger, error_logger


class ChattyMeteo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chatty-meteo", description="Show the weather for a city and date"
    )
    @app_commands.describe(
        citta="City name",
        giorno="oggi, domani, dopodomani or date (YYYY-MM-DD or DD-MM-YYYY)",
    )
    @handle_errors("chatty-meteo")
    async def weather_command(
        self,
        interaction: discord.Interaction,
        citta: str,
        giorno: Optional[str] = "oggi",
    ):
        await interaction.response.defer()
        giorno = giorno.lower().strip()
        today = datetime.now()

        try:
            if giorno == "oggi":
                requested_date = today
            elif giorno == "domani":
                requested_date = today + timedelta(days=1)
            elif giorno == "dopodomani":
                requested_date = today + timedelta(days=2)
            else:
                parts = giorno.split("-")
                if len(parts[0]) == 4:
                    requested_date = datetime.strptime(giorno, "%Y-%m-%d")
                elif len(parts[2]) == 4:
                    requested_date = datetime.strptime(giorno, "%d-%m-%Y")
                else:
                    raise ValueError

        except Exception:
            error_logger.warning(
                "Invalid date format from %s: %s", interaction.user.display_name, giorno
            )
            await interaction.followup.send(t("invalid_date"))
            return

        # --- LOG Weather Request ---
        channel_name = (
            interaction.channel.name if hasattr(interaction.channel, "name") else "DM"
        )
        bot_logger.info(
            "Weather requested by %s (ID: %s) in [%s]: city='%s', date='%s'",
            interaction.user.display_name,
            interaction.user.id,
            channel_name,
            citta,
            requested_date.date(),
        )

        weather_response = await get_weather(citta, requested_date.date())
        await interaction.followup.send(weather_response)


async def setup(bot):
    await bot.add_cog(ChattyMeteo(bot))
