import sqlite3
import os
import sys

from utils.localization import detect_system_language, load_language, t

load_language(detect_system_language())


DB_FILE = "chatty.db"

if not os.path.isfile(DB_FILE):
    print(t("db_missing"))
    sys.exit(1)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

def show_menu():
    print()
    print(t("menu_title"))
    print(t("menu_option_1"))
    print(t("menu_option_2"))
    print(t("menu_option_3"))
    print(t("menu_option_4"))

def print_results(rows):
    if not rows:
        print(t("no_results"))
        return
    for row in rows:
        print("-" * 50)
        print(t("result_header", timestamp=row[1], username=row[2], user_id=row[3], channel=row[4]))
        print(t("result_message", message=row[5]))
        print(t("result_response", response=row[6]))

try:
    while True:
        show_menu()
        choice = input(f"\n{t('input_select_option')}").strip()

        if choice == "1":
            cursor.execute("SELECT * FROM conversations ORDER BY id DESC LIMIT 10")
            results = cursor.fetchall()
            print_results(results)

        elif choice == "2":
            username = input(t("input_username")).strip()
            cursor.execute("SELECT * FROM conversations WHERE user = ? ORDER BY id DESC LIMIT 10", (username,))
            results = cursor.fetchall()
            print_results(results)

        elif choice == "3":
            query = input(t("input_sql_query")).strip()
            confirm = input(t("input_confirm_query")).strip().lower()
            if confirm == "y":
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    print_results(results)
                except Exception as e:
                    print(t("query_error", error=e))
            else:
                print(t("query_cancelled"))

        elif choice == "4":
            print(t("exit_message"))
            break

        else:
            print(t("invalid_choice"))

finally:
    conn.close()
    print(t("db_closed"))
