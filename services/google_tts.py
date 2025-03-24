import tempfile
from gtts import gTTS

from utils.logger import service_logger, error_logger
from utils.config import DEFAULT_TTS_LANG


def generate_tts_audio(text, language=DEFAULT_TTS_LANG):
    """
    Generate an MP3 audio file from text using Google Text-to-Speech (gTTS).

    Args:
        text (str): The text to convert to audio.
        language (str): The language for TTS. Default from config.

    Returns:
        str | None: Path to the generated audio file, or None on error.
    """
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            preview = text[:30] + "..." if len(text) > 30 else text
            service_logger.info(
                "TTS audio generated for: '%s' [Lang: %s]", preview, language
            )
            return fp.name
    except Exception as e:
        error_logger.error("TTS generation failed: %s", str(e))
        return None
