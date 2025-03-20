from flask import Flask, render_template_string, request
import threading
from db_utils import cursor
from gemini_utils import MODEL
from memory import user_memory
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
    <p>Active model: <strong>{{ model }}</strong></p>
    <p>Users in memory: {{ users }}</p>
    <p>Total conversations: {{ total_conversations }}</p>

    <h2>📅 Daily activity (last 7 days)</h2>
    <ul>
        {% for day, count in activity %}
        <li>{{ day }}: {{ count }} messages</li>
        {% endfor %}
    </ul>

    <h2>🔍 Filter conversations by user</h2>
    <form method="get" action="/">
        <input type="text" name="user_filter" placeholder="Username">
        <button type="submit">Filter</button>
    </form>

    <h2>Last 10 conversations{% if user_filter %} by {{ user_filter }}{% endif %}</h2>
    <ul>
        {% for row in conversations %}
        <li><strong>{{ row[1] }}</strong> - {{ row[2] }}:<br><b>💬</b> {{ row[5] }}<br><b>🤖</b> {{ row[6] }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    user_filter = request.args.get("user_filter")

    if user_filter:
        cursor.execute("SELECT * FROM conversations WHERE user = ? ORDER BY id DESC LIMIT 10", (user_filter,))
    else:
        cursor.execute("SELECT * FROM conversations ORDER BY id DESC LIMIT 10")
    conversations = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_conversations = cursor.fetchone()[0]

    cursor.execute("SELECT DATE(timestamp) as day, COUNT(*) FROM conversations GROUP BY day ORDER BY day DESC LIMIT 7")
    activity = cursor.fetchall()

    return render_template_string(
        TEMPLATE,
        model=MODEL,
        users=len(user_memory),
        total_conversations=total_conversations,
        conversations=conversations,
        activity=activity,
        user_filter=user_filter
    )

def start_dashboard():
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
