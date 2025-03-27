# telegram_commands/chatty_wiki.py

from telegram.helpers import escape_markdown
from telegram.ext import CommandHandler

from utils.localization import translate
from utils.logger import bot_logger
from core.handler import fetch_wikipedia

BOT_COMMAND = "chatty_wiki"


async def chatty_wiki(update, context):
    """
    Handle the /chatty_wiki command: searches Wikipedia for the provided term and sends the summary.

    Args:
        update (Update): Telegram update object containing the search term.
        context (ContextTypes.DEFAULT_TYPE): The context passed by the handler.
    """
    if not context.args:
        await update.message.reply_text(translate("wiki_usage"))
        return

    text_raw = update.message.text or ""
    term = text_raw.replace("/" + BOT_COMMAND, "", 1).strip()
    bot_logger.info("Wikipedia search for: %s", term)

    title, description, link, image = await fetch_wikipedia(term)

    if title is None:
        await update.message.reply_text(description)  # Already localized error
        return

    response = f"📚 *{escape_markdown(title, version=2)}*\n\n{escape_markdown(description, version=2)}"
    if link:
        response += f"\n\n🔗 {escape_markdown(link, version=2)}"

    await update.message.reply_text(response, parse_mode="MarkdownV2")


def register(app):
    app.add_handler(CommandHandler(BOT_COMMAND, chatty_wiki))
