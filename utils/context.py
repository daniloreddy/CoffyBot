import json
import os

from utils.logger import bot_logger

CONTEXT_FILE = "config/context.json"
PROMPT_DIR = "prompts"


def save_context_to_file():
    """Save the current server_context dictionary to context.json."""
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(server_context, f, indent=4)


def get_context_prompt(server_name: str) -> str:
    """Return the context prompt for the given server, and log the file used."""
    filename = server_context.get(server_name)
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
    """Set a context prompt file for the given server. Return True if successful."""
    path = os.path.join(PROMPT_DIR, filename)
    if os.path.isfile(path):
        server_context[server_name] = filename
        save_context_to_file()
        bot_logger.info("Context file '%s' set for server '%s'", filename, server_name)
        return True
    return False


def reset_context(server_name: str):
    """Reset context for a server (remove entry)."""
    if server_name in server_context:
        del server_context[server_name]
        save_context_to_file()


# Load context.json at startup or create empty
if os.path.isfile(CONTEXT_FILE):
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        server_context = json.load(f)
else:
    server_context = {}
    save_context_to_file()  # Crea file vuoto
    bot_logger.info("Context file not found, created empty context.json")
