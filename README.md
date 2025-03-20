# ☕ CoffyBot – Discord AI Companion

![CoffyBot](https://img.shields.io/badge/CoffyBot-AI%20Discord%20Bot-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> Un bot Discord potenziato con intelligenza artificiale che fornisce chat, meteo, TTS, immagini AI e tanto altro. Minimal, potente e 100% personalizzabile.

---

## 🚀 Funzionalità Principali
- 💬 **Chat AI (Gemini)** ➜ risponde con IA Google Gemini, supporta allegati PDF, TXT, DOCX, HTML, CSV, ODT.
- 🌦️ **Meteo** ➜ previsioni per oggi, domani, dopodomani o data specifica (es: `22-03-2025`).
- 🗣️ **TTS** ➜ genera audio MP3 da testo.
- 🖼️ **Immagini AI** ➜ genera immagini da prompt (Stable Diffusion via Hugging Face).
- 🧠 **Memoria utente** ➜ mantiene il contesto delle conversazioni.
- 🗄️ **Log su database** ➜ tutte le chat vengono loggate in `chatty.db`.
- 📊 **Dashboard Web** ➜ attività live via browser ([localhost:5000](http://localhost:5000)).
- 🧹 **Reset memoria** ➜ comando per pulire la memoria chat.
- 🔐 **Comandi admin-only** ➜ gestione ruoli + fallback ID.

---

## 📂 Struttura Progetto
- `bot.py` ➜ core bot, comandi slash
- `services_utils.py` ➜ funzioni meteo, TTS, immagini, admin-check
- `memory.py` ➜ gestione memoria utente
- `db_utils.py` ➜ logging SQLite
- `dashboard.py` ➜ Flask dashboard web
- `chatty.env` ➜ variabili API (non incluso)
- `chatty.env.bat` ➜ variabili API per Windows (non incluso)

---

## ⚙️ Installazione
```bash
# Clona il progetto
git clone https://github.com/TUO_USERNAME/coffybot.git
cd coffybot

# Crea ambiente virtuale
python3 -m venv coffy-env
source coffy-env/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

### 🖥️ Avvio Bot
```bash
# Linux
./chatty.sh

# Windows
chatty.bat
```

---

## 📦 Requisiti (requirements.txt)
```text
discord.py
python-dotenv
requests
gtts
beautifulsoup4
python-docx
odfpy
PyMuPDF
flask
```

---

## 🔐 Configura `chatty.env`
```env
BOT_TOKEN=Inserisci_il_token_discord
GEMINI_API_KEY=Chiave_Gemini
OPENWEATHER_API_KEY=Chiave_OpenWeather
HUGGINGFACE_API_KEY=Chiave_HuggingFace
FALLBACK_ID=Tuoi_ID_Discord
```

---

## 🛡️ Comandi Principali
| Comando Slash        | Descrizione                                     |
|----------------------|-------------------------------------------------|
| `/chatty`            | Chatta con Coffy (allegati supportati)         |
| `/chatty-wiki`       | Cerca su Wikipedia                             |
| `/chatty-meteo`      | Mostra meteo con data personalizzata           |
| `/chatty-tts`        | Genera audio da testo                          |
| `/chatty-image`      | Genera immagine AI                             |
| `/chatty-reset`      | Azzera la memoria utente (admin only)          |
| `/chatty-info`       | Info su modello e memoria                      |
| `/chatty-model`      | Cambia modello Gemini (admin only)             |

---

## 🕵️ Debug nascosto (incognito mode)
Messaggio testuale:
```
chatty debug admininfo
```

---

## 📝 Licenza
MIT License - Free to use & customize.

---

> Made with ☕ by ChatGPT - Powered by voglia di spaccare su Discord.  
> **DAJEEE!**
