import tempfile

from gtts import gTTS
from utils.logger import service_logger, error_logger


# --- Google TTS ---
def generate_tts_audio(text, language="it"):
    """
    Generate an MP3 audio file from text using Google Text-to-Speech (gTTS).

    Args:
        text (str): The text to convert to audio.
        language (str): The language for TTS. Default is 'it' (Italian).

    Returns:
        str | None: Path to the generated audio file, or None on error.
    """
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            service_logger.info(
                "TTS audio generated for text: '%s' [Lang: %s]", text[:50], language
            )
            return fp.name
    except Exception as e:
        error_logger.error("TTS generation failed: %s", str(e))
        return None
