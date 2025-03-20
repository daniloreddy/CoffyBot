import sqlite3
import os
import sys

DB_FILE = "chatty.db"

if not os.path.isfile(DB_FILE):
    print("❌ The database chatty.db does not exist in the current folder.")
    sys.exit(1)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

def show_menu():
    print("\n📊 Coffy Query Tool - chatty.db")
    print("1. View the last 10 conversations")
    print("2. Search by username")
    print("3. Enter custom SQL query")
    print("4. Exit")

def print_results(rows):
    if not rows:
        print("⚠️ No results found.")
        return
    for row in rows:
        print("-" * 50)
        print(f"🕒 {row[1]} - 👤 {row[2]} ({row[3]}) - 📢 #{row[4]}")
        print(f"💬 Message: {row[5]}")
        print(f"🤖 Response: {row[6]}")

try:
    while True:
        show_menu()
        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            cursor.execute("SELECT * FROM conversations ORDER BY id DESC LIMIT 10")
            results = cursor.fetchall()
            print_results(results)

        elif choice == "2":
            username = input("Enter the username to search: ").strip()
            cursor.execute("SELECT * FROM conversations WHERE user = ? ORDER BY id DESC LIMIT 10", (username,))
            results = cursor.fetchall()
            print_results(results)

        elif choice == "3":
            query = input("Enter your SQL query: ").strip()
            confirm = input("⚠️ Do you want to execute this query? (y/n): ").strip().lower()
            if confirm == "y":
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    print_results(results)
                except Exception as e:
                    print(f"❌ Query error: {e}")
            else:
                print("❌ Query cancelled.")

        elif choice == "4":
            print("👋 Exiting the tool. See you next time!")
            break

        else:
            print("⚠️ Invalid choice. Please try again.")

finally:
    conn.close()
    print("🔒 Database connection closed.")
