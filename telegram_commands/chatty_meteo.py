# telegram_commands/chatty_meteo.py

import re

from telegram.ext import CommandHandler
from datetime import datetime, timedelta

from core.handler import fetch_weather
from utils.localization import translate
from utils.logger import bot_logger


def parse_date(date_str):
    """
    Convert input string into a datetime.date object.
    """

    date_str = date_str.lower().strip()
    today = datetime.now().date()

    if date_str == "oggi":
        return today
    elif date_str == "domani":
        return today + timedelta(days=1)
    elif date_str == "dopodomani":
        return today + timedelta(days=2)

    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def extract_city_and_date(args):
    if not args:
        return "", "oggi"

    potential_date = args[-1].lower()
    city_tokens = args[:-1]

    if potential_date in ["oggi", "domani", "dopodomani"]:
        return " ".join(city_tokens), potential_date

    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            datetime.strptime(potential_date, fmt)
            return " ".join(city_tokens), potential_date
        except ValueError:
            continue

    return " ".join(args), "oggi"  # default if no date found


async def chatty_meteo(update, context):
    """
    Handle the /chatty_meteo command: provides weather forecast for a city and optional date.

    Args:
        update (Update): Telegram update object containing the city and optional date.
        context (ContextTypes.DEFAULT_TYPE): The context passed by the handler.
    """
    raw_args = update.message.text.split()[1:]  # Remove command name
    city, date_input = extract_city_and_date(raw_args)
    date_parsed = parse_date(date_input)

    if not city:
        await update.message.reply_text(translate("meteo_usage"))
        return

    if not date_parsed:
        await update.message.reply_text(translate("meteo_invalid_date"))
        return

    bot_logger.info("Weather request: city='%s', date='%s'", city, date_parsed)
    result = await fetch_weather(city, date_parsed)

    await update.message.reply_text(result)


def register(app):
    app.add_handler(CommandHandler("chatty_meteo", chatty_meteo))
