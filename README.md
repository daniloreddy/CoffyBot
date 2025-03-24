# Coffy Discord Bot

**Coffy** is a private Discord bot powered by Google Gemini models. It can generate AI responses, images, and audio, fetch weather data, search Wikipedia, and includes advanced admin commands for server customization and monitoring.

---

## 🚀 Features

- 🤖 Chat with Google Gemini (via `/chatty`)
- 🖼️ Generate images using Stable Diffusion (Hugging Face API)
- 🔊 Text-to-Speech audio generation (Google TTS)
- ☁️ Weather forecast from OpenWeather
- 📚 Wikipedia search
- 🛠️ Admin commands via DM (model switch, logs, context management)

---

## 📂 Project Structure

```
/bot.py                 # Main bot script
/utils/                 # Configuration, logging, context, helpers
/services/              # API integrations (Gemini, TTS, Weather, etc.)
/cogs/                  # Discord command modules (COGs)
/tools/                 # Utility tools (key checker, DB helper)
```

---

## ⚙️ Setup Guide

1. Create a `.env` file in the root directory with your API keys and settings:
```
BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_google_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
FALLBACK_ID=your_discord_user_id
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python bot.py
```

---

## 🌐 Localization

All user-facing messages are localized via JSON files in the `/lang/` directory.  
Use `tools/key_verification_tool.py` to detect unused or missing translation keys.

Default language: **English**  
Languages can be added via additional JSON files: `en.json`, `it.json`, etc.

---

## 📊 Logs

Log files are saved in the `/logs/` directory:
- `bot.log` ➔ General events and commands
- `services.log` ➔ External API calls
- `errors.log` ➔ Errors and exceptions

---

## 🧹 Context System

Each server can have a **custom AI context** stored in `/prompts/`.  
Admins can assign these contexts using the `/chatty-admin-context` command.

Context file format: plain `.txt`, content is prepended to each AI prompt.

---

## 🛠️ Admin Features

Available via private messages (DM) only:
- Switch Gemini model
- View last conversations
- Activity stats (last 7 days)
- View/set/reset server context
- List supported models and context files

Admin access is role-based (`Admin`, `Boss`, `CoffyMaster`) or by fallback ID.

---

## 🧠 Memory Note

Coffy does **not store conversation history**.  
Each interaction is processed independently, using only context (if set).

---

## 📬 Contact

Developed by [Your Name or Discord Tag].  
For issues or requests, contact me directly.
