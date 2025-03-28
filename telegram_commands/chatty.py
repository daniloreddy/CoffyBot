# telegram_commands/chatty.py

from telegram.ext import CommandHandler, MessageHandler, filters
from core.handler import process_text

from utils.context import get_context_prompt
from utils.localization import translate
from utils.logger import bot_logger
from utils.generic import read_file_content, resolve_server_name
from utils.db_utils import log_to_sqlite

BOT_COMMAND = "chatty"


async def chatty(update, context):
    """
    Handle the /chatty command: sends the user's prompt to Gemini, including attachments if present.

    Args:
        update (Update): Telegram update object containing the message.
        context (ContextTypes.DEFAULT_TYPE): The context passed by the handler.
    """
    user = update.effective_user
    chat = update.effective_chat

    # Raccogli testo principale
    text_raw = update.message.text or ""
    prompt_text = text_raw.replace("/" + BOT_COMMAND, "", 1).strip()

    # Raccogli eventuali allegati
    attachment_texts = []

    if update.message.document:
        document = update.message.document
        if document.file_name.lower().endswith(
            (".txt", ".csv", ".html", ".pdf", ".docx", ".odt")
        ):
            file = await document.get_file()
            file_bytes = await file.download_as_bytearray()

            # Telegram non ha Attachment come Discord, usiamo workaround
            class FakeAttachment:
                def __init__(self, filename, file_bytes):
                    self.filename = filename
                    self._file_bytes = file_bytes
                    self.size = len(file_bytes)

                async def read(self):
                    return self._file_bytes

            fake = FakeAttachment(document.file_name, file_bytes)
            result = await read_file_content(fake)
            if not result.startswith(("❌", "⚠️")):
                attachment_texts.append(result)

    if not prompt_text and not attachment_texts:
        await update.message.reply_text(translate("generic_no_text"))
        return

    final_prompt = prompt_text
    if attachment_texts:
        final_prompt += (
            "\n\n"
            + translate("attachment_content")
            + "\n"
            + "\n".join(attachment_texts)
        )

    server_name = resolve_server_name(user, chat)
    context_prompt = get_context_prompt(server_name)

    if context_prompt:
        full_prompt = context_prompt.strip() + "\n\n" + final_prompt
        bot_logger.info("Context applied for Telegram user/group: %s", server_name)
    else:
        full_prompt = final_prompt

    bot_logger.info("Gemini prompt from %s: %s", user.full_name, prompt_text[:100])
    response = process_text(full_prompt)

    log_to_sqlite(user, chat, final_prompt, response)

    if response:
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(translate("gemini_error"))


def register(app):
    app.add_handler(
        MessageHandler(
            filters.Document.ALL | (filters.TEXT & filters.Command(BOT_COMMAND)), chatty
        )
    )
