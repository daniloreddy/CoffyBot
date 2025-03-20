import json
import os
import time
from collections import deque

MEMORY_FILE = "memory.json"
MEMORY_TIMEOUT = 600
MAX_MEMORY = 5
user_memory = {}

if os.path.isfile(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            data = json.load(f)
            for uid, d in data.items():
                user_memory[uid] = {"exchanges": deque(d["exchanges"], maxlen=MAX_MEMORY), "timestamp": d["timestamp"]}
        except Exception:
            user_memory = {}

def save_memory_to_file():
    data = {uid: {"exchanges": list(d["exchanges"]), "timestamp": d["timestamp"]} for uid, d in user_memory.items()}
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def update_memory(user_id, question, now):
    if user_id in user_memory and now - user_memory[user_id]["timestamp"] > MEMORY_TIMEOUT:
        user_memory.pop(user_id)

    if user_id not in user_memory:
        user_memory[user_id] = {"exchanges": deque(maxlen=MAX_MEMORY), "timestamp": now}
    user_memory[user_id]["timestamp"] = now

    prompt = ""
    for exchange in user_memory[user_id]["exchanges"]:
        prompt += f"User: {exchange['question']}\nCoffy: {exchange['answer']}\n"
    prompt += f"User: {question}\nCoffy:"
    return prompt
