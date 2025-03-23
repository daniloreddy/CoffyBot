import json
import os

from collections import deque
from utils.localization import t
from utils.logger import bot_logger

MEMORY_FILE = "config/memory.json"
MEMORY_TIMEOUT = 600
MAX_MEMORY = 5
user_memory = {}

if os.path.isfile(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            data = json.load(f)
            for uid, d in data.items():
                user_memory[uid] = {
                    "exchanges": deque(d["exchanges"], maxlen=MAX_MEMORY),
                    "timestamp": d["timestamp"],
                }
        except Exception:
            user_memory = {}


def save_memory_to_file():
    """
    Save the current user memory to disk in JSON format.

    Converts deque objects to lists for serialization.
    """

    data = {
        uid: {"exchanges": list(d["exchanges"]), "timestamp": d["timestamp"]}
        for uid, d in user_memory.items()
    }
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)
    bot_logger.info("Memory saved to %s", MEMORY_FILE)


def update_memory(user_id, question, now):
    """
    Update or initialize the memory for a user and generate a prompt.

    Args:
        user_id (str): The Discord user ID.
        question (str): The new user question.
        now (float): Current timestamp.

    Returns:
        str: Generated prompt including past exchanges and the new question.
    """

    if (
        user_id in user_memory
        and now - user_memory[user_id]["timestamp"] > MEMORY_TIMEOUT
    ):
        user_memory.pop(user_id)

    if user_id not in user_memory:
        user_memory[user_id] = {"exchanges": deque(maxlen=MAX_MEMORY), "timestamp": now}
    user_memory[user_id]["timestamp"] = now

    prompt = ""
    for exchange in user_memory[user_id]["exchanges"]:
        prompt += f"{t('memory_user_label')}: {exchange['question']}\n{t('memory_bot_label')}: {exchange['answer']}\n"
    prompt += f"{t('memory_user_label')}: {question}\n{t('memory_bot_label')}:"
    return prompt
