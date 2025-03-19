from flask import Flask, render_template_string, request
import threading
from db_utils import cursor
from gemini_utils import MODEL
from memory import memoria_utente
import sqlite3

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Coffy Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
        h1 { color: #343a40; }
        ul { list-style: none; padding: 0; }
        li { background: #fff; padding: 10px; margin: 5px 0; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        form { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>📊 Coffy Dashboard</h1>
    <p>Modello attivo: <strong>{{ model }}</strong></p>
    <p>Utenti in memoria: {{ users }}</p>
    <p>Totale conversazioni: {{ total_conversations }}</p>

    <h2>📅 Attività giornaliera (ultimi 7 giorni)</h2>
    <ul>
        {% for giorno, conteggio in attivita %}
        <li>{{ giorno }}: {{ conteggio }} messaggi</li>
        {% endfor %}
    </ul>

    <h2>🔍 Filtra conversazioni per utente</h2>
    <form method="get" action="/">
        <input type="text" name="utente" placeholder="Nome utente">
        <button type="submit">Filtra</button>
    </form>

    <h2>Ultime 10 conversazioni{% if filtro %} di {{ filtro }}{% endif %}</h2>
    <ul>
        {% for row in conversazioni %}
        <li><strong>{{ row[1] }}</strong> - {{ row[2] }}:<br><b>💬</b> {{ row[5] }}<br><b>🤖</b> {{ row[6] }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    filtro = request.args.get("utente")

    if filtro:
        cursor.execute("SELECT * FROM conversazioni WHERE user = ? ORDER BY id DESC LIMIT 10", (filtro,))
    else:
        cursor.execute("SELECT * FROM conversazioni ORDER BY id DESC LIMIT 10")
    conversazioni = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM conversazioni")
    total_conversations = cursor.fetchone()[0]

    cursor.execute("SELECT DATE(timestamp) as giorno, COUNT(*) FROM conversazioni GROUP BY giorno ORDER BY giorno DESC LIMIT 7")
    attivita = cursor.fetchall()

    return render_template_string(TEMPLATE, model=MODEL, users=len(memoria_utente), total_conversations=total_conversations, conversazioni=conversazioni, attivita=attivita, filtro=filtro)

def start_dashboard():
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()

