# Coffy Bot (Discord + Telegram)

**Coffy** is a private multi-platform bot powered by Google Gemini.  
It supports both **Discord** and **Telegram**, offering AI-powered chat, Wikipedia search, weather forecast, TTS audio, and powerful admin tools for context management, logs and stats.

---

## 🚀 Features

- 🤖 Chat with Google Gemini (`/chatty`)
- 🌍 Weather forecast from OpenWeather
- 📚 Wikipedia search
- 🔊 Text-to-Speech audio (Google TTS)
- 🔒 Localized command restriction (e.g. DM-only, admin-only)
- 🛠️ Advanced admin commands (context, models, stats, logs)

> ❌ **Image generation** has been removed due to quality and reliability issues.

---

## 📦 Project Structure

```
/bot_launcher.py        # Main launcher (runs Discord, Telegram or both)
/bot_discord.py         # Discord bot entry point
/bot_telegram.py        # Telegram bot entry point

/cogs/                  # Discord command modules (slash commands)
/telegram_commands/     # Telegram command modules

/utils/                 # Config, logging, localization, context utils
/services/              # External API integrations (Gemini, TTS, etc.)
/core/                  # Central logic handler

/tools/                 # Extra utilities (DB checker, translation keys)
/lang/                  # Localized strings (e.g., en.json, it.json)
/logs/                  # Logs for bot, services, errors
/prompts/               # Custom context files
```

---

## ⚙️ Setup Guide

1. Create a `.env` file in the root directory with your API keys:
```
DISCORD_BOT_TOKEN=your_discord_bot_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_google_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

DISCORD_FALLBACK_ID=your_discord_user_id
TELEGRAM_FALLBACK_ID=your_telegram_username
```

2. Create and activate the virtual environment:
```bash
python -m venv coffy-env
source coffy-env/bin/activate  # On Windows: coffy-env\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Launch the bot(s) using the unified launcher:
```bash
python bot_launcher.py discord         # Start Discord bot only
python bot_launcher.py telegram        # Start Telegram bot only
python bot_launcher.py discord telegram  # Start both
```

---

## 🌐 Localization

All bot messages are fully localized using JSON language files in `/lang/`.  
Languages supported: **English (en)** and **Italian (it)**.  
Add new languages via additional files like `fr.json`, `de.json`, etc.

Use:
```bash
python tools/key_verification_tool.py
```
to check for missing or unused keys.

---

## 📊 Logging

Log files are saved in the `/logs/` folder:

- `bot.log` → Events and commands
- `services.log` → External API usage
- `errors.log` → Errors and exceptions

Each log is timestamped and auto-rotated.

---

## 🧠 Context System

Each Discord server or Telegram group can define a custom **context prompt** stored in `/prompts/`.  
It will be prepended to every user query sent to Gemini.

Admins can set or reset contexts using:
- `/chatty-admin-context`
- `/chatty-admin-context-reset`

---

## 🛠️ Admin Commands

Commands available via **DM only** (Telegram: by fallback username):

- `/chatty-admin-model` ➜ Switch Gemini model
- `/chatty-admin-models` ➜ List available models
- `/chatty-admin-context` ➜ Set server context
- `/chatty-admin-context-reset` ➜ Reset server context
- `/chatty-admin-contexts` ➜ List available contexts
- `/chatty-admin-stats` ➜ Show usage statistics
- `/chatty-admin-activity` ➜ Daily usage stats
- `/chatty-admin-lastlogs` ➜ Show last 10 prompts
- `/chatty-admin-help` ➜ Show help for admin commands

---

## 🤖 Telegram Command Mapping

Telegram does not support dashes (`-`) in command names, so all Discord commands are mapped with underscores (`_`):

| Discord Command        | Telegram Command          |
|------------------------|---------------------------|
| `/chatty`              | `/chatty`                |
| `/chatty-help`         | `/chatty_help`           |
| `/chatty-info`         | `/chatty_info`           |
| `/chatty-meteo`        | `/chatty_meteo`          |
| `/chatty-tts`          | `/chatty_tts`            |
| `/chatty-wiki`         | `/chatty_wiki`           |
| `/chatty-admin-*`      | `/chatty_admin_*`        |

---

## 📬 Contact

Developed by OpenAI ChatGPT with supervision of DaniloReddy.  
For issues or requests, contact me directly.