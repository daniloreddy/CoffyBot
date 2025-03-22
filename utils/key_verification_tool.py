import json
import re
import os

from collections import Counter

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_FILE = os.path.normpath(os.path.join(BASE_DIR, "../lang/en.json"))
CODE_DIR = os.path.normpath(os.path.join(BASE_DIR, "../"))
EXCLUDED_DIRS = {"venv", "env", "__pycache__", ".git", "site-packages"}

# --- Load JSON keys ---
with open(LANG_FILE, "r", encoding="utf-8") as f:
    lang_keys = set(json.load(f).keys())

# --- Extract keys used in t("...") ---
used_keys = set()
all_matches = []  # Store all matches for duplicate detection
pattern = re.compile(r't\(\s*["\']([a-zA-Z0-9_\.\-]+)["\']', re.MULTILINE)

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
                    all_matches.extend(matches)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# --- Duplicate detection ---
key_counter = Counter(all_matches)
duplicates = [key for key, count in key_counter.items() if count > 1]

# --- Comparison ---
missing_keys = used_keys - lang_keys
unused_keys = lang_keys - used_keys

# --- Output results ---
print("\nLanguage key check complete!")
print(f"Used keys in code: {len(used_keys)}")
print(f"Keys in {LANG_FILE}: {len(lang_keys)}")

if missing_keys:
    print(f"\n❌ Missing keys in {LANG_FILE} ({len(missing_keys)}):")
    for key in sorted(missing_keys):
        print(f" - {key}")
else:
    print("\n✅ No missing keys!")

if unused_keys:
    print(f"\n🟡 Unused keys in {LANG_FILE} ({len(unused_keys)}):")
    for key in sorted(unused_keys):
        print(f" - {key}")
else:
    print("\n✅ No unused keys!")

if duplicates:
    print(f"\n🔁 Duplicate keys used in code ({len(duplicates)}):")
    for key in sorted(duplicates):
        print(f" - {key}")
else:
    print("\n✅ No duplicate keys used in code!")
