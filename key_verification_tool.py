import json
import re
import os

# --- Config ---
LANG_FILE = "lang/en.json"  # Path to your en.json
CODE_DIR = "."  # Root directory to scan for .py files
EXCLUDED_DIRS = {"venv", "env", "__pycache__", ".git", "site-packages"}

# --- Load JSON keys ---
with open(LANG_FILE, "r", encoding="utf-8") as f:
    lang_keys = set(json.load(f).keys())

# --- Extract keys used in t("...") ---
used_keys = set()
pattern = re.compile(r"\bt\([\"\']([a-zA-Z0-9_\.\-]+)[\"\']")

for root, dirs, files in os.walk(CODE_DIR):
    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]  # Skip unwanted dirs
    for file in files:
        if file.endswith(".py") and file != os.path.basename(__file__):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    used_keys.update(matches)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# --- Comparison ---
missing_keys = used_keys - lang_keys
unused_keys = lang_keys - used_keys

print("\nLanguage key check complete!")
print(f"Used keys in code: {len(used_keys)}")
print(f"Keys in {LANG_FILE}: {len(lang_keys)}")

if missing_keys:
    print(f"\nMissing keys in {LANG_FILE} ({len(missing_keys)}):")
    for key in sorted(missing_keys):
        print(f" - {key}")
else:
    print("\nNo missing keys!")

if unused_keys:
    print(f"\nUnused keys in {LANG_FILE} ({len(unused_keys)}):")
    for key in sorted(unused_keys):
        print(f" - {key}")
else:
    print("\nNo unused keys!")