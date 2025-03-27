# core/handler.py

"""
Central logic module for processing user inputs and delegating to services.
This decouples bot commands from the implementation details of each feature.
"""

from services.gemini import get_gemini_response
from services.google_tts import generate_tts_audio
from services.weather import get_weather as weather_service
from services.wikipedia import search_wikipedia as wikipedia_service
from utils.logger import service_logger


def process_text(prompt: str, context: str = None) -> str | None:
    """
    Generate a Gemini AI response from the provided prompt and optional context.

    Args:
        prompt (str): The user message or query.
        context (str, optional): Optional context string to prepend.

    Returns:
        str | None: The generated response text, or None on failure.
    """
    final_prompt = f"{context.strip()}\n\n{prompt}" if context else prompt
    service_logger.info("Processing Gemini prompt (len=%d)", len(final_prompt))
    return get_gemini_response(final_prompt)


def process_tts(text: str) -> str | None:
    """
    Convert text to speech and return the path to the MP3 audio file.

    Args:
        text (str): The input text to convert to speech.

    Returns:
        str | None: Path to the generated audio file, or None on failure.
    """
    preview = text[:30] + "..." if len(text) > 30 else text
    service_logger.info("Processing TTS for: '%s'", preview)
    return generate_tts_audio(text)


async def fetch_weather(city: str, date=None) -> str:
    """
    Retrieve weather forecast or current data for a given city and optional date.

    Args:
        city (str): Name of the city to retrieve weather for.
        date (str, optional): Date for the forecast (e.g., 'oggi', 'domani', or YYYY-MM-DD).

    Returns:
        str: Formatted weather information, or an error message.
    """
    service_logger.info("Fetching weather for city='%s', date='%s'", city, date)
    return await weather_service(city, date)


async def fetch_wikipedia(term: str) -> str:
    """
    Retrieve a summary from Wikipedia for a given search term.

    Args:
        term (str): The topic or term to search on Wikipedia.

    Returns:
        str: Summary or error message from Wikipedia.
    """
    service_logger.info("Searching Wikipedia for term='%s'", term)
    return await wikipedia_service(term)
