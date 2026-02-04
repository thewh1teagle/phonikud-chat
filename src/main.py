"""
Hebrew Voice Assistant CLI

TTS models:
    wget https://github.com/thewh1teagle/style-onnx/releases/download/model-files-v1.0/636_female_style.npy
    wget https://github.com/thewh1teagle/style-onnx/releases/download/model-files-v1.0/libritts_hebrew.onnx
    wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx

STT (Sonara server, separate terminal):
    wget https://github.com/thewh1teagle/sonara/releases/download/v0.1.0/sonara-linux-arm64
    tar xf sonara-linux-arm64
    ./sonara pull https://huggingface.co/ivrit-ai/whisper-large-v3-turbo-ggml/resolve/main/ggml-model.bin?download=true
    ./sonara serve ./ggml-model.bin

    ollama pull gemma3:4b
    uv run src/main.py
"""

import sys
import os

import sounddevice as sd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recorder import wait_for_key, record
from tts import create_audio
from stt import transcribe
from agent.ask import ask

BANNER = """
========================================
  Hebrew Voice Assistant
========================================

Hold [R] to record | [Q] to quit
"""


def _select_audio_devices():
    devices = sd.query_devices()
    default_in, default_out = sd.default.device

    print("\nInput devices:")
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            mark = "*" if idx == default_in else " "
            print(f"{mark} {idx}: {dev['name']}")

    raw_in = input("Select mic index (Enter for default): ").strip()
    in_device = default_in
    if raw_in:
        in_device = int(raw_in)

    print("\nOutput devices:")
    for idx, dev in enumerate(devices):
        if dev.get("max_output_channels", 0) > 0:
            mark = "*" if idx == default_out else " "
            print(f"{mark} {idx}: {dev['name']}")

    raw_out = input("Select speaker index (Enter for default): ").strip()
    out_device = default_out
    if raw_out:
        out_device = int(raw_out)

    sd.default.device = (in_device, out_device)
    os.environ["AUDIO_INPUT_DEVICE"] = str(in_device)
    print(f"\nUsing mic={in_device}, speaker={out_device}\n")


def main():
    print(BANNER)
    _select_audio_devices()

    while True:
        key = wait_for_key()
        if key == "q":
            break

        path = record()
        if not path:
            print("No audio recorded.")
            continue

        print("Transcribing...")
        try:
            text = transcribe(path)
        finally:
            if os.path.exists(path):
                os.remove(path)
        print(f"You: {text}")

        if not text.strip():
            print("No speech detected.")
            continue

        print("Thinking...")
        response = ask(text)
        print(f"AI: {response}")

        print("Speaking...")
        samples, sr = create_audio(response)
        sd.play(samples, sr)
        sd.wait()

        print("\nHold [R] to record | [Q] to quit\n")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
