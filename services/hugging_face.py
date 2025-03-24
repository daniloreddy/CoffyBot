import aiohttp
import tempfile

from utils.logger import service_logger, error_logger
from utils.config import HUGGINGFACE_API_KEY, HF_MODEL_URL


async def generate_image(prompt):
    """
    Generate an image using Hugging Face Stable Diffusion API (Async).

    Args:
        prompt (str): The prompt describing the image to generate.

    Returns:
        str | None: Path to the generated image file, or status string ("loading"/"limit")/None on error.
    """
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                HF_MODEL_URL, headers=headers, json=payload
            ) as response:
                preview = prompt[:30] + "..." if len(prompt) > 30 else prompt

                if response.status == 200:
                    content = await response.read()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as fp:
                        fp.write(content)
                        service_logger.info("Image generated for prompt: '%s'", preview)
                        return fp.name

                elif response.status == 503:
                    service_logger.warning(
                        "Hugging Face model loading... prompt: '%s'", preview
                    )
                    return "loading"

                elif response.status == 429:
                    service_logger.warning(
                        "Hugging Face API rate limit hit. Prompt: '%s'", preview
                    )
                    return "limit"

                else:
                    text = await response.text()
                    error_logger.error(
                        "Hugging Face API error [%s]: %s", response.status, text
                    )
                    return None

    except Exception as e:
        error_logger.error("Image generation failed: %s", str(e))
        return None
