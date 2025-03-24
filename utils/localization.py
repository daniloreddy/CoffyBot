import locale
import json
import os

from utils.config import LANG_DIR, DEFAULT_LANG

language_cache = {}


def detect_system_language():
    """
    Detect the system language based on locale settings.

    Returns:
        str: Language code (e.g., 'it', 'en'), default is 'en'.
    """
    lang, _ = locale.getdefaultlocale()
    if lang:
        return lang.split("_")[0].lower()
    return DEFAULT_LANG


def load_language(lang_code):
    """
    Load the translation JSON file for the specified language.

    Args:
        lang_code (str): Language code.

    Returns:
        dict: Dictionary of translation keys and values.
    """
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
    """
    Translate a key using the loaded language file, with optional formatting.

    Args:
        key (str): Translation key.
        lang (str): Language code. Defaults to 'en'.
        **kwargs: Optional formatting arguments for the text.

    Returns:
        str: Translated and formatted string.
    """
    translations = load_language(lang)
    text = translations.get(key, f"[{key}]")
    return text.format(**kwargs)
