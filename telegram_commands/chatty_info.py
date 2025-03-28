# telegram_commands/chatty_info.py

import time

from telegram.ext import CommandHandler

from utils.localization import translate
from utils.logger import bot_logger
from utils.context import get_context_prompt
from utils.generic import resolve_server_name
from services.gemini import get_current_model
from utils.config import BOT_START_TIME


async def chatty_info(update, context):
    """
    Handle the /chatty_info command: sends bot uptime, model and version info.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): The context passed by the handler.
    """
    uptime_seconds = int(time.time() - BOT_START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours >= 24:
        days, hours = divmod(hours, 24)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    else:
        uptime_str = f"{hours}h {minutes}m {seconds}s"

    server_name = resolve_server_name(update.effective_user, update.effective_chat)
    context_file = "Active" if get_context_prompt(server_name) else "None"

    msg = translate(
        "info_message",
        model=get_current_model(),
        context=context_file,
        uptime=uptime_str,
    )

    await update.message.reply_text(msg)


def register(app):
    app.add_handler(CommandHandler("chatty_info", chatty_info))
