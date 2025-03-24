import json
import os

from utils.logger import bot_logger
from utils.config import CONTEXT_FILE, PROMPT_DIR


def get_server_context():
    """
    Load the current context mapping from disk.

    Returns:
        dict: Mapping of server_name -> context filename.
    """
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        bot_logger.error("Failed to load context: %s", str(e))
        return {}


def save_context_to_file(context: dict):
    """
    Save the given context mapping to disk.

    Args:
        context (dict): Mapping of server_name -> context filename.
    """
    try:
        with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=4)
    except Exception as e:
        bot_logger.error("Failed to save context: %s", str(e))


def get_context_prompt(server_name: str) -> str:
    """
    Return the context prompt for the given server, and log the file used.

    Args:
        server_name (str): The name of the server.

    Returns:
        str: The context prompt content, or empty string if not found.
    """
    context = get_server_context()
    filename = context.get(server_name)
    if not filename:
        return ""

    path = os.path.join(PROMPT_DIR, filename)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                bot_logger.info(
                    "Context file '%s' applied for server '%s'", filename, server_name
                )
                return content
        except Exception as e:
            bot_logger.error(
                "Failed to load context file '%s' for server '%s': %s",
                filename,
                server_name,
                str(e),
            )
            return ""
    else:
        bot_logger.warning(
            "Context file '%s' not found for server '%s'", filename, server_name
        )
        return ""


def set_context_file(server_name: str, filename: str) -> bool:
    """
    Associate a context file with a server and save the mapping.

    Args:
        server_name (str): The server's name.
        filename (str): The context file to associate.

    Returns:
        bool: True if successful, False otherwise.
    """
    path = os.path.join(PROMPT_DIR, filename)
    if os.path.isfile(path):
        context = get_server_context()
        context[server_name] = filename
        save_context_to_file(context)
        bot_logger.info("Context file '%s' set for server '%s'", filename, server_name)
        return True
    else:
        bot_logger.warning(
            "Attempted to set non-existent context file '%s' for server '%s'",
            filename,
            server_name,
        )
        return False


def reset_context(server_name: str):
    """
    Remove the context association for a server.

    Args:
        server_name (str): The server's name.
    """
    context = get_server_context()
    if server_name in context:
        del context[server_name]
        save_context_to_file(context)
        bot_logger.info("Context reset for server '%s'", server_name)
