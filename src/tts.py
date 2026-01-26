from kokoro_onnx import Kokoro
from misaki import en, espeak

_kokoro = None
_g2p = None

DEFAULT_VOICE = "af_heart"
_voice_override = None


def _init():
    global _kokoro, _g2p
    if _kokoro is None:
        _kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
        fallback = espeak.EspeakFallback(british=False)
        _g2p = en.G2P(trf=False, british=False, fallback=fallback)


def set_voice(voice):
    global _voice_override
    _voice_override = voice


def create_audio(text, speed=1.0):
    global _voice_override
    _init()
    voice = _voice_override or DEFAULT_VOICE
    _voice_override = None
    phonemes, _ = _g2p(text)
    samples, sample_rate = _kokoro.create(phonemes, voice, is_phonemes=True, speed=speed)
    return samples, sample_rate