import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils.localization import t
from utils.logger import service_logger, error_logger  # Universal loggers

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-1.5-flash"


def change_model(name):
    """
    Change the Gemini model used by the bot.

    Args:
        name (str): Name of the new model.

    Returns:
        bool: True if model is changed, False if invalid name.
    """
    global MODEL
    if name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        MODEL = name
        service_logger.info("Gemini model changed to: %s", MODEL)
        return True
    else:
        error_logger.warning("Attempted to switch to invalid model: %s", name)
        return False


def get_gemini_response(prompt):
    """
    Generate a response from Gemini model.

    Args:
        prompt (str): Prompt text for the AI model.

    Returns:
        str: Generated response text or error message.
    """
    try:
        model_instance = genai.GenerativeModel(MODEL)
        response = model_instance.generate_content(prompt)
        service_logger.info("Gemini response generated with model: %s", MODEL)
        return response.text
    except Exception as e:
        error_logger.error("Gemini API error: %s", str(e))
        return t("gemini_error", error=e)
