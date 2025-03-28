# utils/generic.py

import asyncio
import os
import functools
import discord
import io
import fitz  # PyMuPDF

from bs4 import BeautifulSoup
from docx import Document
from odf.opendocument import load
from odf.text import P
from telegram import Update, User, Chat
from telegram.ext import ContextTypes
from discord import Interaction


from utils.localization import translate
from utils.logger import bot_logger
from utils.config import (
    DISCORD_ADMIN_ROLES,
    DISCORD_FALLBACK_ID,
    MAX_PDF_SIZE,
    MAX_TXT_CSV_HTML_SIZE,
    DISCORD_FALLBACK_ID,
    TELEGRAM_FALLBACK_ID,
)


async def check_discord_admin(interaction) -> bool:
    """
    Check if the user invoking the command is the Discord fallback admin.

    Args:
        interaction: The Discord interaction object.

    Returns:
        bool: True if admin, False otherwise (also sends error message).
    """
    if interaction.user.id != DISCORD_FALLBACK_ID:
        await interaction.response.send_message(
            translate("admin_only_command"), ephemeral=True
        )
        return False
    return True


async def check_discord_dm(interaction) -> bool:
    """
    Check if the command is used in a direct message (DM).

    Args:
        interaction: The Discord interaction object.

    Returns:
        bool: True if DM, False otherwise (also sends error message).
    """
    if interaction.guild is not None:
        await interaction.response.send_message(
            translate("private_only"), ephemeral=True
        )
        return False
    return True


async def check_telegram_admin(update: Update) -> bool:
    """
    Check if the user is the Telegram fallback admin.

    Args:
        update (Update): Telegram update object.

    Returns:
        bool: True if admin, False otherwise (and sends error message).
    """
    username = update.effective_user.username
    if username != TELEGRAM_FALLBACK_ID:
        await update.message.reply_text(translate("admin_only_command"))
        return False
    return True


async def check_telegram_dm(update: Update) -> bool:
    """
    Check if the command is used in a private Telegram chat.

    Args:
        update (Update): Telegram update object.

    Returns:
        bool: True if DM, False otherwise (and sends error message).
    """
    if update.effective_chat.type != "private":
        await update.message.reply_text(translate("private_only"))
        return False
    return True


def resolve_server_name(user: User, chat: Chat) -> str:
    """
    Return a consistent server_name based on chat type (group or private).
    """
    if chat.type in ("group", "supergroup"):
        return chat.title or f"Group-{chat.id}"
    else:
        return user.username or f"User-{user.id}"


async def read_file_content(attachment):
    """
    Read the content of a supported file attachment.

    Supports TXT, CSV, HTML, PDF, DOCX, ODT formats with size limits.
    Converts content to plain text.

    Args:
        attachment (discord.Attachment): The uploaded file.

    Returns:
        str: Extracted text or error message.
    """
    try:
        filename = attachment.filename.lower()
        if filename.endswith((".txt", ".csv", ".html")):
            if attachment.size <= MAX_TXT_CSV_HTML_SIZE:
                file_bytes = await attachment.read()
                if filename.endswith(".html"):
                    soup = BeautifulSoup(file_bytes, "html.parser")
                    return soup.get_text()
                return file_bytes.decode("utf-8", errors="ignore")
            else:
                return translate("file_too_large_small", filename=filename)

        elif filename.endswith(".pdf"):
            if attachment.size <= MAX_PDF_SIZE:
                file_bytes = await attachment.read()
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    text = "".join([page.get_text() for page in doc])
                    return text[:5000]
            else:
                return translate("file_too_large_pdf", filename=filename)

        elif filename.endswith(".docx"):
            file_bytes = await attachment.read()
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs])
            return text[:5000]

        elif filename.endswith(".odt"):
            file_bytes = await attachment.read()
            odt_doc = load(io.BytesIO(file_bytes))
            text = "\n".join([str(p) for p in odt_doc.getElementsByType(P)])
            return text[:5000]

        else:
            return translate("file_format_not_supported", filename=filename)

    except Exception as e:
        return translate("file_reading_error", error=e)


def handle_errors(command_name: str):
    """
    Decorator to handle exceptions in Discord commands.

    Logs the error and sends a localized error message to the user.

    Args:
        command_name (str): Name of the command for logging.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(interaction, *args, **kwargs):
            try:
                await func(interaction, *args, **kwargs)
            except Exception as e:
                bot_logger.error("Error in command %s: %s", command_name, str(e))
                try:
                    if interaction.response.is_done():
                        await interaction.followup.send(translate("generic_error"))
                    else:
                        await interaction.response.send_message(
                            translate("generic_error"), ephemeral=True
                        )
                except Exception:
                    bot_logger.error("Failed to send error message to user.")

        return wrapper

    return decorator


async def check_admin(interaction, fallback_id: int = DISCORD_FALLBACK_ID) -> bool:
    """
    Check if the user invoking the command has admin privileges.

    Args:
        interaction (Interaction): The command interaction.
        fallback_id (int): User ID fallback if roles are not present.

    Returns:
        bool: True if admin, False otherwise.
    """

    try:
        if any(role.name in DISCORD_ADMIN_ROLES for role in interaction.user.roles):
            return True
    except AttributeError:
        bot_logger.warning(translate("admin_role_fallback"))

    if interaction.user.id == fallback_id:
        return True

    await interaction.response.send_message(
        translate("admin_only_command"), ephemeral=True
    )
    return False


def is_dm_only(interaction) -> bool:
    """
    Check if a command is used in direct messages.

    Args:
        interaction (Interaction): The command interaction.

    Returns:
        bool: True if DM, else sends warning and returns False.
    """

    if interaction.guild is None:
        return True
    asyncio.create_task(
        interaction.response.send_message(translate("dm_only_command"), ephemeral=True)
    )
    return False


def safe_delete(filepath: str):
    """Delete a file if it exists, safely."""
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
    except Exception:
        pass
