import locale
import json
import os

LANG_DIR = "lang"  # Directory with  en.json, it.json, etc.
DEFAULT_LANG = "en"
translations = {}
language_cache = {}

def detect_system_language():
    lang, _ = locale.getdefaultlocale()  # Example: ('it_IT', 'UTF-8')
    if lang:
        return lang.split('_')[0].lower()  # → 'it'
    return "en"  # Default fallback


def load_language(lang_code):
    if lang_code in language_cache:
        return language_cache[lang_code]
    path = os.path.join(LANG_DIR, f"{lang_code}.json")
    if not os.path.isfile(path):
        path = os.path.join(LANG_DIR, f"{DEFAULT_LANG}.json")
    with open(path, "r", encoding="utf-8") as f:
        translations = json.load(f)
        language_cache[lang_code] = translations
        return translations

def t(key, lang="en", **kwargs):
    translations = load_language(lang)
    text = translations.get(key, f"[{key}]")
    return text.format(**kwargs)

