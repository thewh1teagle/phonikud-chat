from pywhispercpp.model import Model

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = Model("ggml-large-v3-turbo-q8_0.bin")
    return _model


def transcribe(audio_path):
    model = _get_model()
    segments = model.transcribe(audio_path, language="en")
    return " ".join(segment.text for segment in segments).strip()

