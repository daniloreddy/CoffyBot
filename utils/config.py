# utils/config.py

import os
import time

from dotenv import load_dotenv

load_dotenv()

BOT_START_TIME = time.time()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- General Settings ---
DEFAULT_LANG = "en"
LANG_DIR = os.path.normpath(os.path.join(BASE_DIR, "../lang"))
if not os.path.exists(LANG_DIR):
    os.makedirs(LANG_DIR)
PROMPT_DIR = os.path.normpath(os.path.join(BASE_DIR, "../prompts"))
if not os.path.exists(PROMPT_DIR):
    os.makedirs(PROMPT_DIR)
CONTEXT_FILE = os.path.normpath(os.path.join(BASE_DIR, "../config/context.json"))

# --- File Size Limits (bytes) ---
MAX_TXT_CSV_HTML_SIZE = 20 * 1024  # 20 KB
MAX_PDF_SIZE = 1 * 1024 * 1024  # 1 MB
MAX_DOC_LENGTH = 5000  # Truncate long content

# --- Admin Settings ---
DISCORD_ADMIN_ROLES = ["Admin", "Boss", "CoffyMaster"]
DISCORD_FALLBACK_ID = int(
    os.getenv("DISCORD_FALLBACK_ID", "123456789012345678")
)  # Default fallback ID
TELEGRAM_FALLBACK_ID = os.getenv(
    "TELEGRAM_FALLBACK_ID", "daniloreddy"
)  # Default fallback ID

# --- Logging ---
LOG_DIR = os.path.normpath(os.path.join(BASE_DIR, "../logs"))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
BOT_LOG_FILE = "bot.log"
SERVICE_LOG_FILE = "services.log"
ERROR_LOG_FILE = "errors.log"

# --- DB ---
DB_FILE = os.path.normpath(os.path.join(BASE_DIR, "../chatty.db"))

# --- API Keys ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Hugging Face ---
HF_MODEL_URL = (
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
)

# --- Gemini ---
MODELS_FILE = os.path.normpath(os.path.join(BASE_DIR, "../config/models.json"))
DEFAULT_MODEL = "gemini-1.5-flash"

# --- Weather ---
WEATHER_EMOJIS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "fog": "🌫️",
    "haze": "🌫️",
}

# --- TTS ---
DEFAULT_TTS_LANG = "it"
