import os
import functools
import logging
import discord
import io
import fitz  # PyMuPDF
import logging

from bs4 import BeautifulSoup
from docx import Document
from odf.opendocument import load
from odf.text import P

from utils.localization import t

# --- Read Attached File Content ---
async def read_file_content(attachment):
    try:
        filename = attachment.filename.lower()
        if filename.endswith(".txt") or filename.endswith(".csv"):
            if attachment.size <= 20480:
                file_bytes = await attachment.read()
                return file_bytes.decode("utf-8", errors="ignore")
            else:
                return t("file_too_large_small", filename=filename)

        elif filename.endswith(".html"):
            if attachment.size <= 20480:
                file_bytes = await attachment.read()
                soup = BeautifulSoup(file_bytes, "html.parser")
                return soup.get_text()
            else:
                return t("file_too_large_small", filename=filename)

        elif filename.endswith(".pdf"):
            if attachment.size <= 1048576:
                file_bytes = await attachment.read()
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    text = "".join([page.get_text() for page in doc])
                    return text[:5000]
            else:
                return t("file_too_large_pdf", filename=filename)

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
            return t("file_format_not_supported", filename=filename)

    except Exception as e:
        return t("file_reading_error", error=e)

def handle_errors(command_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            try:
                await func(interaction, *args, **kwargs)
            except Exception as e:
                logging.error("Error in command %s: %s", command_name, str(e))
                try:
                    if interaction.response.is_done():
                        await interaction.followup.send(t("generic_error"))
                    else:
                        await interaction.response.send_message(t("generic_error"), ephemeral=True)
                except Exception as inner_err:
                    logging.error("Error in command %s: %s", command_name, str(e))
        return wrapper
    return decorator

# --- Admin Role Check ---
ADMIN_ROLES = ["Admin", "Boss", "CoffyMaster"]
FALLBACK_ID = int(os.getenv("FALLBACK_ID"))


async def check_admin(interaction, fallback_id: int = FALLBACK_ID) -> bool:
    try:
        if any(role.name in ADMIN_ROLES for role in interaction.user.roles):
            return True
    except AttributeError:
        logging.warning(t("admin_role_fallback"))

    if interaction.user.id == fallback_id:
        return True

    await interaction.response.send_message(t("admin_only_command"), ephemeral=True)
    return False