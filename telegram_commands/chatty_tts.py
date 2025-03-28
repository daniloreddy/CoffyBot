# telegram_commands/chatty_tts.py

import os

from telegram.ext import CommandHandler
from telegram import InputFile

from core.handler import process_tts
from utils.logger import bot_logger, error_logger
from utils.localization import translate
from utils.generic import safe_delete

BOT_COMMAND = "chatty_tts"


async def chatty_tts(update, context):
    """
    Handle the /chatty_tts command: converts the given text to audio using Google TTS and sends it back.

    Args:
        update (Update): Telegram update object containing the text.
        context (ContextTypes.DEFAULT_TYPE): The context passed by the handler.
    """
    raw = update.message.text or ""
    text = raw.replace("/" + BOT_COMMAND, "", 1).strip()

    if not text:
        await update.message.reply_text(translate("tts_no_text"))
        return

    bot_logger.info(
        "TTS requested by %s (%s): '%s'",
        update.effective_user.full_name,
        update.effective_user.username,
        text,
    )

    audio_file = process_tts(text)

    if audio_file and os.path.isfile(audio_file):
        try:

            with open(audio_file, "rb") as f:
                audio_input = InputFile(f, filename="tts.mp3")
                await update.message.reply_audio(audio=audio_input)

            safe_delete(audio_file)
            bot_logger.info("TTS sent successfully for: %s", text)
        except Exception as e:
            error_logger.error("Telegram failed to send TTS: %s", str(e))
            await update.message.reply_text(translate("tts_error"))
    else:
        error_logger.error("TTS failed for %s", update.effective_user.full_name)
        await update.message.reply_text(translate("tts_error"))


def register(app):
    app.add_handler(CommandHandler(BOT_COMMAND, chatty_tts))
