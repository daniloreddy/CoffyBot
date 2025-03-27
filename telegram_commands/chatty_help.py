# telegram_commands/chatty_help.py

from telegram.ext import CommandHandler

from utils.localization import translate
from utils.logger import bot_logger


async def chatty_help(update, context):
    """
    Handle the /chatty_help command: sends a list of available bot commands and their descriptions.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): The context passed by the handler.
    """
    await update.message.reply_text(translate("help_message_telegram"))


def register(app):
    app.add_handler(CommandHandler("chatty_help", chatty_help))
