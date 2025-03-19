# packages
import requests
import os
import tempfile
import csv
import io
import asyncio
import fitz  # PyMuPDF
import logging

# namespaces
from dotenv import load_dotenv
from gtts import gTTS
from bs4 import BeautifulSoup
from docx import Document
from odf.opendocument import load
from odf.text import P
from datetime import datetime, timedelta

# carica le variabili di ambiente
load_dotenv()

# --- Controllo ruolo ADmin ---
RUOLI_ADMIN = ["Admin", "Boss", "CoffyMaster"]
FALLBACK_ID = int(os.getenv("FALLBACK_ID"))

async def check_admin(interaction, fallback_id: int = FALLBACK_ID) -> bool:
    try:
        if any(role.name in RUOLI_ADMIN for role in interaction.user.roles):
            return True
    except AttributeError:
        logging.warning("⚠️ Impossibile accedere ai ruoli. Uso fallback ID.")

    if interaction.user.id == fallback_id:
        return True

    await interaction.response.send_message("⛔ Solo admin può usare questo comando.", ephemeral=True)
    return False

# --- Wikipedia ---
def cerca_wikipedia(termine):
    try:
        url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{termine.replace(' ', '_')}"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            titolo = data.get("title", "Sconosciuto")
            estratto = data.get("extract", "Nessuna descrizione trovata.")
            link = data.get("content_urls", {}).get("desktop", {}).get("page", "")
            immagine = data.get("thumbnail", {}).get("source")
            return titolo, estratto, link, immagine
        else:
            return None, "❌ Nessuna voce trovata.", "", None
    except Exception as e:
        return None, f"❌ Errore Wikipedia: {e}", "", None

# --- Meteo ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EMOJI_METEO = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "fog": "🌫️",
    "haze": "🌫️"
}

def ottieni_meteo(citta, data=None):
    try:
        if data is None or data == datetime.now().date():
            # Meteo attuale
            url = f"https://api.openweathermap.org/data/2.5/weather?q={citta}&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
            r = requests.get(url)
            if r.status_code == 200:
                data_json = r.json()
                temp = data_json['main']['temp']
                descrizione = data_json['weather'][0]['description'].capitalize()
                condizione = data_json['weather'][0]['main'].lower()
                umidita = data_json['main']['humidity']
                vento = data_json['wind']['speed']
                paese = data_json['sys']['country']
                emoji = EMOJI_METEO.get(condizione, "🌍")
                return f"📍 {citta.title()}, {paese} {emoji}\n🌡️ {temp} °C | {descrizione}\n💧 Umidità: {umidita}% | 🌬️ Vento: {vento} m/s"
            else:
                return "❌ Città non trovata o errore nell'API."
        else:
            # Previsioni future
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={citta}&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
            r = requests.get(url)
            if r.status_code != 200:
                return "❌ Città non trovata o errore nell'API."

            dati = r.json()
            previsione_trovata = None

            for entry in dati["list"]:
                dt_txt = entry["dt_txt"]  # formato: "2025-03-22 15:00:00"
                dt_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                if dt_obj.date() == data and dt_obj.hour == 12:
                    previsione_trovata = entry
                    break

            if not previsione_trovata:
                return f"⚠️ Nessuna previsione trovata per il {data.strftime('%d-%m-%Y')}."

            temp = previsione_trovata['main']['temp']
            descrizione = previsione_trovata['weather'][0]['description'].capitalize()
            condizione = previsione_trovata['weather'][0]['main'].lower()
            umidita = previsione_trovata['main']['humidity']
            vento = previsione_trovata['wind']['speed']
            paese = dati['city']['country']
            emoji = EMOJI_METEO.get(condizione, "🌍")

            return f"📍 {citta.title()}, {paese} {emoji} - {data.strftime('%d-%m-%Y')}\n🌡️ {temp} °C | {descrizione}\n💧 Umidità: {umidita}% | 🌬️ Vento: {vento} m/s"

    except Exception as e:
        return f"❌ Errore meteo: {e}"

# --- Google TTS ---
def genera_audio_tts(testo, lingua="it"):
    try:
        tts = gTTS(text=testo, lang=lingua)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        print(f"Errore TTS: {e}")
        return None


# --- Generazione Immagini ---
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
def genera_immagine(prompt):
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": prompt}
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as fp:
                fp.write(response.content)
                return fp.name
        elif response.status_code == 503:
            print("❌ Il modello è in caricamento. Riprova tra qualche istante.")
            return "loading"
        elif response.status_code == 429:
            print("❌ Limite di utilizzo Hugging Face raggiunto.")
            return "limit"
        else:
            print(f"Errore API Hugging Face: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Errore immagine: {e}")
        return None

# --- Lettura contenuti allegati ---
async def leggi_contenuto_file(allegato):
    try:
        nome = allegato.filename.lower()
        if nome.endswith(".txt") or nome.endswith(".csv"):
            if allegato.size <= 20480:
                file_bytes = await allegato.read()
                return file_bytes.decode("utf-8", errors="ignore")
            else:
                return f"⚠️ Il file '{nome}' è troppo grande. Max 20KB."

        elif nome.endswith(".html"):
            if allegato.size <= 20480:
                file_bytes = await allegato.read()
                soup = BeautifulSoup(file_bytes, "html.parser")
                return soup.get_text()
            else:
                return f"⚠️ Il file HTML '{nome}' è troppo grande. Max 20KB."

        elif nome.endswith(".pdf"):
            if allegato.size <= 1048576:
                file_bytes = await allegato.read()
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    testo = "".join([page.get_text() for page in doc])
                    return testo[:5000]  # Limite di sicurezza
            else:
                return f"⚠️ Il PDF '{nome}' è troppo grande. Max 1MB."

        elif nome.endswith(".docx"):
            file_bytes = await allegato.read()
            doc = Document(io.BytesIO(file_bytes))
            testo = "\n".join([p.text for p in doc.paragraphs])
            return testo[:5000]

        elif nome.endswith(".odt"):
            file_bytes = await allegato.read()
            odt_doc = load(io.BytesIO(file_bytes))
            testo = "\n".join([str(p) for p in odt_doc.getElementsByType(P)])
            return testo[:5000]

        else:
            return f"❌ Formato file '{nome}' non supportato."

    except Exception as e:
        return f"❌ Errore nella lettura del file: {e}"
    