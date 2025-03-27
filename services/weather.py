# services/weather.py

import aiohttp
from datetime import datetime

from utils.config import OPENWEATHER_API_KEY, WEATHER_EMOJIS
from utils.localization import translate
from utils.logger import service_logger, error_logger


async def fetch_weather_data(session, url):
    """
    Fetch weather data from a given URL using an aiohttp session.

    Args:
        session (aiohttp.ClientSession): The aiohttp session to use.
        url (str): The URL to request weather data from.

    Returns:
        dict | None: Parsed JSON data if successful, or None on error.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                text = await response.text()
                error_logger.error("Weather API error [%s]: %s", response.status, text)
                return None
    except Exception as e:
        error_logger.error("Weather fetch error: %s", str(e))
        return None


def format_weather_response(
    temp, description, condition, humidity, wind, city, country, date=None
):
    """
    Format weather data into a readable string with emojis and metrics.
    """
    emoji = WEATHER_EMOJIS.get(condition, "🌍")
    date_str = f" - {date.strftime('%d-%m-%Y')}" if date else ""
    return (
        f"📍 {city.title()}, {country} {emoji}{date_str}\n"
        f"🌡️ {temp} °C | {description}\n"
        f"💧 Humidity: {humidity}% | 🌬️ Wind: {wind} m/s"
    )


async def get_weather(city, date=None):
    """
    Get current weather or forecast for a given city and optional date.

    Args:
        city (str): The city to get weather data for.
        date (datetime.date, optional): Date for forecast; None for current weather.

    Returns:
        str: Weather report string, or error message on failure.
    """
    try:
        async with aiohttp.ClientSession() as session:
            if date is None or date == datetime.now().date():
                # Current weather
                url = (
                    f"https://api.openweathermap.org/data/2.5/weather?q={city}"
                    f"&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
                )
                data = await fetch_weather_data(session, url)
                if not data:
                    return translate("weather_city_not_found")

                service_logger.info("Weather data fetched for city: %s", city)
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"].capitalize()
                condition = data["weather"][0]["main"].lower()
                humidity = data["main"]["humidity"]
                wind = data["wind"]["speed"]
                country = data["sys"]["country"]
                return format_weather_response(
                    temp, description, condition, humidity, wind, city, country
                )

            else:
                # Forecast
                url = (
                    f"http://api.openweathermap.org/data/2.5/forecast?q={city}"
                    f"&appid={OPENWEATHER_API_KEY}&units=metric&lang=it"
                )
                data = await fetch_weather_data(session, url)
                if not data:
                    return translate("weather_city_not_found")

                selected = None
                for entry in data["list"]:
                    dt_obj = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    if dt_obj.date() == date and dt_obj.hour == 12:
                        selected = entry
                        break

                if not selected:
                    return translate(
                        "weather_no_forecast", date=date.strftime("%d-%m-%Y")
                    )

                service_logger.info("Weather forecast fetched for %s (%s)", city, date)
                temp = selected["main"]["temp"]
                description = selected["weather"][0]["description"].capitalize()
                condition = selected["weather"][0]["main"].lower()
                humidity = selected["main"]["humidity"]
                wind = selected["wind"]["speed"]
                country = data["city"]["country"]
                return format_weather_response(
                    temp, description, condition, humidity, wind, city, country, date
                )

    except Exception as e:
        error_logger.error("Weather service error: %s", str(e))
        return translate("weather_error", error=e)
