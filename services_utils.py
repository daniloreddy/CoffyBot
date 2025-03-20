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

# Load environment variables
load_dotenv()

# --- Admin Role Check ---
ADMIN_ROLES = ["Admin", "Boss", "CoffyMaster"]
FALLBACK_ID = int(os.getenv("FALLBACK_ID"))

async def check_admin(interaction, fallback_id: int = FALLBACK_ID) -> bool:
    try:
        if any(role.name in ADMIN_ROLES for role in interaction.user.roles):
            return True
    except AttributeError:
        logging.warning("⚠️ Cannot access user roles. Using fallback ID.")

    if interaction.user.id == fallback_id:
        return True

    await interaction.response.send_message("⛔ Only admin can use this command.", ephemeral=True)
    return False

# --- Wikipedia ---
def search_wikipedia(term):
    try:
        url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{term.replace(' ', '_')}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Unknown")
            extract = data.get("extract", "No description found.")
            link = data.get("content_urls", {}).get("desktop", {}).get("page", "")
            image = data.get("thumbnail", {}).get("source")
            return title, extract, link, image
        else:
            return None, "❌ No entry found.", "", None
    except Exception as e:
        return None, f"❌ Wikipedia error: {e}", "", None

# --- Weather ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_EMOJIS = {
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

def get_weather(city, date=None):
    try:
        if date is None or date == datetime.now().date():
            # Current weather
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
            response = requests.get(url)
            if response.status_code == 200:
                data_json = response.json()
                temp = data_json['main']['temp']
                description = data_json['weather'][0]['description'].capitalize()
                condition = data_json['weather'][0]['main'].lower()
                humidity = data_json['main']['humidity']
                wind = data_json['wind']['speed']
                country = data_json['sys']['country']
                emoji = WEATHER_EMOJIS.get(condition, "🌍")
                return f"📍 {city.title()}, {country} {emoji}\n🌡️ {temp} °C | {description}\n💧 Humidity: {humidity}% | 🌬️ Wind: {wind} m/s"
            else:
                return "❌ City not found or API error."
        else:
            # Future forecast
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
            response = requests.get(url)
            if response.status_code != 200:
                return "❌ City not found or API error."

            forecast_data = response.json()
            selected_forecast = None

            for entry in forecast_data["list"]:
                dt_txt = entry["dt_txt"]  # format: "2025-03-22 15:00:00"
                dt_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                if dt_obj.date() == date and dt_obj.hour == 12:
                    selected_forecast = entry
                    break

            if not selected_forecast:
                return f"⚠️ No forecast found for {date.strftime('%d-%m-%Y')}."

            temp = selected_forecast['main']['temp']
            description = selected_forecast['weather'][0]['description'].capitalize()
            condition = selected_forecast['weather'][0]['main'].lower()
            humidity = selected_forecast['main']['humidity']
            wind = selected_forecast['wind']['speed']
            country = forecast_data['city']['country']
            emoji = WEATHER_EMOJIS.get(condition, "🌍")

            return f"📍 {city.title()}, {country} {emoji} - {date.strftime('%d-%m-%Y')}\n🌡️ {temp} °C | {description}\n💧 Humidity: {humidity}% | 🌬️ Wind: {wind} m/s"

    except Exception as e:
        return f"❌ Weather error: {e}"

# --- Google TTS ---
def generate_tts_audio(text, language="it"):
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# --- Image Generation ---
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
def generate_image(prompt):
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
            print("❌ Model is loading. Try again shortly.")
            return "loading"
        elif response.status_code == 429:
            print("❌ Hugging Face usage limit reached.")
            return "limit"
        else:
            print(f"Hugging Face API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

# --- Read Attached File Content ---
async def read_file_content(attachment):
    try:
        filename = attachment.filename.lower()
        if filename.endswith(".txt") or filename.endswith(".csv"):
            if attachment.size <= 20480:
                file_bytes = await attachment.read()
                return file_bytes.decode("utf-8", errors="ignore")
            else:
                return f"⚠️ File '{filename}' is too large. Max 20KB."

        elif filename.endswith(".html"):
            if attachment.size <= 20480:
                file_bytes = await attachment.read()
                soup = BeautifulSoup(file_bytes, "html.parser")
                return soup.get_text()
            else:
                return f"⚠️ HTML file '{filename}' is too large. Max 20KB."

        elif filename.endswith(".pdf"):
            if attachment.size <= 1048576:
                file_bytes = await attachment.read()
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    text = "".join([page.get_text() for page in doc])
                    return text[:5000]  # Safety limit
            else:
                return f"⚠️ PDF '{filename}' is too large. Max 1MB."

        elif filename.endswith(".docx"):
            file_bytes = await attachment.read()
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs])
            return text[:5000]

        elif filename.endswith(".odt"):
            file_bytes = await attachment.read()
            odt_doc = load(io.BytesIO(file_bytes))
            text = "\n".join([str(p) for p in odt_doc.getElementsByType(P)])
            return text[:5000]

        else:
            return f"❌ File format '{filename}' not supported."

    except Exception as e:
        return f"❌ File reading error: {e}"
