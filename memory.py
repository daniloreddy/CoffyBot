import json
import os
import time
from collections import deque

MEMORY_FILE = "memoria.json"
MEMORY_TIMEOUT = 600
MAX_MEMORIA = 5
memoria_utente = {}

if os.path.isfile(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            data = json.load(f)
            for uid, d in data.items():
                memoria_utente[uid] = {"scambi": deque(d["scambi"], maxlen=MAX_MEMORIA), "timestamp": d["timestamp"]}
        except Exception:
            memoria_utente = {}

def salva_memoria_file():
    data = {uid: {"scambi": list(d["scambi"]), "timestamp": d["timestamp"]} for uid, d in memoria_utente.items()}
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def aggiorna_memoria(user_id, domanda, now):
    if user_id in memoria_utente and now - memoria_utente[user_id]["timestamp"] > MEMORY_TIMEOUT:
        memoria_utente.pop(user_id)

    if user_id not in memoria_utente:
        memoria_utente[user_id] = {"scambi": deque(maxlen=MAX_MEMORIA), "timestamp": now}
    memoria_utente[user_id]["timestamp"] = now

    prompt = ""
    for scambio in memoria_utente[user_id]["scambi"]:
        prompt += f"Utente: {scambio['domanda']}\nCoffy: {scambio['risposta']}\n"
    prompt += f"Utente: {domanda}\nCoffy:"
    return prompt
