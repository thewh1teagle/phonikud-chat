from kokoro_onnx import Kokoro
from misaki import en, espeak

_kokoro = None
_g2p = None

VOICE = "af_heart"


def _init():
    global _kokoro, _g2p
    if _kokoro is None:
        _kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
        fallback = espeak.EspeakFallback(british=False)
        _g2p = en.G2P(trf=False, british=False, fallback=fallback)


def create_audio(text, speed=1.0):
    _init()
    phonemes, _ = _g2p(text)
    samples, sample_rate = _kokoro.create(phonemes, VOICE, is_phonemes=True, speed=speed)
    return samples, sample_rate