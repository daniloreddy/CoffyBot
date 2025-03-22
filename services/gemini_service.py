import os
import json
import google.generativeai as genai

from dotenv import load_dotenv
from utils.logger import service_logger, error_logger

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
MODELS = "config/models.json"

# Load supported models and last used model from file
try:
    with open(MODELS, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        SUPPORTED_MODELS = config_data.get("gemini_models", [])
        MODEL = config_data.get(
            "last_used_model",
            SUPPORTED_MODELS[0] if SUPPORTED_MODELS else "gemini-1.5-flash",
        )
        if MODEL not in SUPPORTED_MODELS:
            MODEL = SUPPORTED_MODELS[0] if SUPPORTED_MODELS else "gemini-1.5-flash"
    service_logger.info("Supported Gemini models loaded: %s", SUPPORTED_MODELS)
    service_logger.info("Last used model: %s", MODEL)
except Exception as e:
    error_logger.error("Failed to load models: %s", str(e))
    SUPPORTED_MODELS = ["gemini-1.5-flash"]
    MODEL = "gemini-1.5-flash"


def get_supported_models():
    try:
        with open(MODELS, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("gemini_models", [])
    except Exception as e:
        error_logger.error("Failed to load models: %s", str(e))
        return []


def get_current_model():
    try:
        with open(MODELS, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_model = data.get("last_used_model")
            supported = data.get("gemini_models", [])
            if last_model in supported:
                return last_model
            return supported[0] if supported else "gemini-1.5-flash"
    except Exception as e:
        error_logger.error("Failed to get current model: %s", str(e))
        return "gemini-1.5-flash"


def change_model(name):
    supported = get_supported_models()
    if name in supported:
        try:
            with open(MODELS, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data["last_used_model"] = name
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            service_logger.info("Gemini model changed to: %s", name)
            return True
        except Exception as e:
            error_logger.error("Failed to update last_used_model: %s", str(e))
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
        return None
