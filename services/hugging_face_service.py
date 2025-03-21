import requests
import os
import tempfile
from utils.logger import service_logger, error_logger

# --- Image Generation ---
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL_URL = (
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
)


def generate_image(prompt):
    """
    Generate an image using Hugging Face Stable Diffusion API.

    Args:
        prompt (str): The prompt describing the image to generate.

    Returns:
        str | None: Path to the generated image file, or status string ("loading"/"limit")/None on error.
    """
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": prompt}
        response = requests.post(HF_MODEL_URL, headers=headers, json=payload)

        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as fp:
                fp.write(response.content)
                service_logger.info("Image generated for prompt: '%s'", prompt[:50])
                return fp.name

        elif response.status_code == 503:
            service_logger.warning(
                "Hugging Face model loading... prompt: '%s'", prompt[:50]
            )
            return "loading"

        elif response.status_code == 429:
            service_logger.warning(
                "Hugging Face API rate limit hit for prompt: '%s'", prompt[:50]
            )
            return "limit"

        else:
            error_logger.error(
                "Hugging Face API error [%s]: %s", response.status_code, response.text
            )
            return None

    except Exception as e:
        error_logger.error("Image generation failed: %s", str(e))
        return None
