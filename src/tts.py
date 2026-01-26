from style_onnx import StyleTTS2
from phonikud_onnx import Phonikud
from phonikud import phonemize

model_path = "libritts_hebrew.onnx"
nikud_model_path = 'phonikud-1.0.int8.onnx'
styles_path = "636_female_style.npy"
audio_path = "audio.wav"

# Phonemizer setup
phonikud_model = Phonikud(nikud_model_path)


tts = StyleTTS2(model_path, styles_path)


def create_audio(text, speed=1.32):
    vocalized = phonikud_model.add_diacritics(text)
    phonemes = phonemize(vocalized)

    samples, sr = tts.create(phonemes, speed=speed)
    return samples, sr