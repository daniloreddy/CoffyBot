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

from utils.localization import translate
from utils.logger import bot_logger
from utils.config import ADMIN_ROLES, FALLBACK_ID, MAX_PDF_SIZE, MAX_TXT_CSV_HTML_SIZE


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
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
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


async def check_admin(interaction, fallback_id: int = FALLBACK_ID) -> bool:
    """
    Check if the user invoking the command has admin privileges.

    Args:
        interaction (discord.Interaction): The command interaction.
        fallback_id (int): User ID fallback if roles are not present.

    Returns:
        bool: True if admin, False otherwise.
    """

    try:
        if any(role.name in ADMIN_ROLES for role in interaction.user.roles):
            return True
    except AttributeError:
        bot_logger.warning(translate("admin_role_fallback"))

    if interaction.user.id == fallback_id:
        return True

    await interaction.response.send_message(
        translate("admin_only_command"), ephemeral=True
    )
    return False


def is_dm_only(interaction: discord.Interaction) -> bool:
    """
    Check if a command is used in direct messages.

    Args:
        interaction (discord.Interaction): The command interaction.

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
