# services/google_tts.py

import tempfile
import os

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
    if not text.strip():
        error_logger.warning("TTS skipped: empty or whitespace-only text.")
        return None

    try:
        # Use only the temporary filename without opening the file
        tmp_path = tempfile.mktemp(suffix=".mp3")

        tts = gTTS(text=text, lang=language)
        tts.save(tmp_path)

        filesize = os.path.getsize(tmp_path)
        service_logger.info("TTS file generated: %s (%d bytes)", tmp_path, filesize)

        if filesize == 0:
            error_logger.error("TTS generated an empty file: %s", tmp_path)
            return None

        return tmp_path
    except Exception as e:
        error_logger.error("TTS generation failed: %s", str(e))
        return None
