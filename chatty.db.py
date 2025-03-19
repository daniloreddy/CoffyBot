import sqlite3
import os
import sys

DB_FILE = "chatty.db"

if not os.path.isfile(DB_FILE):
    print("❌ Il database chatty.db non esiste nella cartella corrente.")
    sys.exit(1)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

def mostra_menu():
    print("\n📊 Strumento di interrogazione per Coffy - chatty.db")
    print("1. Visualizza le ultime 10 conversazioni")
    print("2. Cerca per nome utente")
    print("3. Inserisci query SQL personalizzata")
    print("4. Esci")

def stampa_risultati(righe):
    if not righe:
        print("⚠️ Nessun risultato trovato.")
        return
    for riga in righe:
        print("-" * 50)
        print(f"🕒 {riga[1]} - 👤 {riga[2]} ({riga[3]}) - 📢 #{riga[4]}")
        print(f"💬 Messaggio: {riga[5]}")
        print(f"🤖 Risposta: {riga[6]}")

try:
    while True:
        mostra_menu()
        scelta = input("\nSeleziona un'opzione (1-4): ").strip()

        if scelta == "1":
            cursor.execute("SELECT * FROM conversazioni ORDER BY id DESC LIMIT 10")
            risultati = cursor.fetchall()
            stampa_risultati(risultati)

        elif scelta == "2":
            nome = input("Inserisci il nome utente da cercare: ").strip()
            cursor.execute("SELECT * FROM conversazioni WHERE user = ? ORDER BY id DESC LIMIT 10", (nome,))
            risultati = cursor.fetchall()
            stampa_risultati(risultati)

        elif scelta == "3":
            query = input("Inserisci la tua query SQL: ").strip()
            conferma = input("⚠️ Vuoi eseguire questa query? (s/n): ").strip().lower()
            if conferma == "s":
                try:
                    cursor.execute(query)
                    risultati = cursor.fetchall()
                    stampa_risultati(risultati)
                except Exception as e:
                    print(f"❌ Errore nella query: {e}")
            else:
                print("❌ Query annullata.")

        elif scelta == "4":
            print("👋 Uscita dal tool. Alla prossima!")
            break

        else:
            print("⚠️ Scelta non valida. Riprova.")

finally:
    conn.close()
    print("🔒 Connessione al database chiusa.")
