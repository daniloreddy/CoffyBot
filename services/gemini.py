import json
import google.generativeai as genai

from utils.config import GEMINI_API_KEY, MODELS_FILE, DEFAULT_MODEL
from utils.logger import service_logger, error_logger

# --- Configure Gemini API ---
genai.configure(api_key=GEMINI_API_KEY)


def load_model_config():
    """Load model configuration from JSON file."""
    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        error_logger.error("Failed to load models file: %s", str(e))
        return {"gemini_models": [DEFAULT_MODEL], "last_used_model": DEFAULT_MODEL}


def get_supported_models():
    """Return list of supported Gemini models."""
    config = load_model_config()
    models = config.get("gemini_models", [DEFAULT_MODEL])
    return models


def get_current_model():
    """Return the last used model, or fallback to first supported."""
    config = load_model_config()
    supported = config.get("gemini_models", [DEFAULT_MODEL])
    last_model = config.get("last_used_model")
    if last_model in supported:
        return last_model
    return supported[0] if supported else DEFAULT_MODEL


def change_model(name):
    """Change the active Gemini model, if valid."""
    supported = get_supported_models()
    if name in supported:
        try:
            config = load_model_config()
            config["last_used_model"] = name
            with open(MODELS_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            service_logger.info("Gemini model changed to: %s", name)
            return True
        except Exception as e:
            error_logger.error("Failed to update last_used_model: %s", str(e))
    else:
        error_logger.warning("Attempted to switch to invalid model: %s", name)
    return False


def get_gemini_response(prompt):
    """
    Generate response from Gemini API using current model.

    Args:
        prompt (str): The full prompt to send.

    Returns:
        str | None: The model's response or None on error.
    """
    model_name = get_current_model()

    preview = prompt[:45] + " [...] " + prompt[-45:] if len(prompt) > 90 else prompt
    service_logger.info("Gemini prompt preview: %s", preview)

    try:
        model_instance = genai.GenerativeModel(model_name)
        response = model_instance.generate_content(prompt)
        service_logger.info("Gemini response generated with model: %s", model_name)
        return response.text
    except Exception as e:
        error_logger.error("Gemini API error: %s", str(e))
        return None
