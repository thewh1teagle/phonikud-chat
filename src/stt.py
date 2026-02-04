import os
from pathlib import Path

from openai import OpenAI

_client = None

SONARA_BASE_URL = os.getenv("SONARA_BASE_URL", "http://localhost:11531/v1")
SONARA_API_KEY = os.getenv("SONARA_API_KEY", "sonara")
SONARA_MODEL = os.getenv("SONARA_MODEL", "ggml-model.bin")
SONARA_LANGUAGE = os.getenv("SONARA_LANGUAGE", "he")


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(base_url=SONARA_BASE_URL, api_key=SONARA_API_KEY)
    return _client


def transcribe(audio_path):
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"audio file not found: {path}")

    client = _get_client()
    with path.open("rb") as f:
        result = client.audio.transcriptions.create(
            model=SONARA_MODEL,
            file=f,
            language=SONARA_LANGUAGE,
        )

    text = getattr(result, "text", "")
    return text.strip()
