import os
import requests

from datetime import datetime
from utils.localization import t

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
    "haze": "🌫️",
}


async def get_weather(city, date=None):
    try:
        if date is None or date == datetime.now().date():
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
            response = requests.get(url)
            if response.status_code == 200:
                data_json = response.json()
                temp = data_json["main"]["temp"]
                description = data_json["weather"][0]["description"].capitalize()
                condition = data_json["weather"][0]["main"].lower()
                humidity = data_json["main"]["humidity"]
                wind = data_json["wind"]["speed"]
                country = data_json["sys"]["country"]
                emoji = WEATHER_EMOJIS.get(condition, "🌍")
                return f"📍 {city.title()}, {country} {emoji}\n🌡️ {temp} °C | {description}\n💧 Humidity: {humidity}% | 🌬️ Wind: {wind} m/s"
            else:
                return t("weather_city_not_found")
        else:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
            response = requests.get(url)
            if response.status_code != 200:
                return t("weather_city_not_found")

            forecast_data = response.json()
            selected_forecast = None

            for entry in forecast_data["list"]:
                dt_txt = entry["dt_txt"]
                dt_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                if dt_obj.date() == date and dt_obj.hour == 12:
                    selected_forecast = entry
                    break

            if not selected_forecast:
                return t("weather_no_forecast", date=date.strftime("%d-%m-%Y"))

            temp = selected_forecast["main"]["temp"]
            description = selected_forecast["weather"][0]["description"].capitalize()
            condition = selected_forecast["weather"][0]["main"].lower()
            humidity = selected_forecast["main"]["humidity"]
            wind = selected_forecast["wind"]["speed"]
            country = forecast_data["city"]["country"]
            emoji = WEATHER_EMOJIS.get(condition, "🌍")

            return f"📍 {city.title()}, {country} {emoji} - {date.strftime('%d-%m-%Y')}\n🌡️ {temp} °C | {description}\n💧 Humidity: {humidity}% | 🌬️ Wind: {wind} m/s"

    except Exception as e:
        return t("weather_error", error=e)
