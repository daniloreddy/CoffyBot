# bot_telegram.py

"""
Telegram bot launcher and command dispatcher for Coffy.
Initializes commands, context resolution, and polling loop.
"""

import logging
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from utils.localization import detect_system_language, load_language
from utils.generic import resolve_server_name
from utils.logger import bot_logger
from core.handler import process_text
from utils.context import get_context_prompt
from utils.config import TELEGRAM_BOT_TOKEN
from utils.localization import translate
from services.gemini import get_current_model
from telegram_commands.chatty_info import register as register_info
from telegram_commands.chatty_help import register as register_help
from telegram_commands.chatty_wiki import register as register_wiki
from telegram_commands.chatty_meteo import register as register_meteo
from telegram_commands.chatty_tts import register as register_tts
from telegram_commands.chatty import register as register_chatty
from telegram_commands.chatty_admin import register as register_admin


from utils.logger import service_logger

# Redirect lower-level Telegram logs to service_logger
telegram_loggers = ["telegram", "telegram.ext", "httpx", "aiohttp.client"]

for name in telegram_loggers:
    logger = logging.getLogger(name)
    logger.handlers = service_logger.handlers
    logger.setLevel(logging.INFO)
    logger.propagate = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to the /start command.
    """
    await update.message.reply_text(translate("start_message"))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles regular user messages sent in private or group chats.
    """
    user = update.effective_user
    text = update.message.text.strip()
    chat = update.effective_chat

    if not text:
        await update.message.reply_text(translate("generic_no_text"))
        return

    if chat.type != "private" and not text.lower().startswith(("chatty", "coffy")):
        return

    server_name = resolve_server_name(user, chat)
    context_prompt = get_context_prompt(server_name)
    response = process_text(text, context_prompt)

    if response:
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(translate("gemini_error"))


async def start_telegram():
    """
    Initializes and starts the Telegram bot using polling (async-compatible).
    """
    if not TELEGRAM_BOT_TOKEN:
        bot_logger.error("❌ TELEGRAM_BOT_TOKEN is empty or missing!")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    bot_logger.info("✅ ApplicationBuilder created")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    register_info(app)
    register_help(app)
    register_wiki(app)
    register_meteo(app)
    register_tts(app)
    register_admin(app)

    register_chatty(app)

    bot_logger.info("Telegram bot started. Model: %s", get_current_model())

    # --- Start polling manually (async-compatible) ---
    await app.initialize()
    await app.start()
    try:
        await app.updater.start_polling()
        await asyncio.Event().wait()  # 🧠 blocks forever until killed
    except asyncio.CancelledError:
        bot_logger.info("Telegram polling task cancelled.")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    load_language(detect_system_language())
    asyncio.run(start_telegram())
