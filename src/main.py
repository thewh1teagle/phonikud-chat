"""
Hebrew Voice Assistant CLI

TTS models:
    wget https://github.com/thewh1teagle/style-onnx/releases/download/model-files-v1.0/636_female_style.npy
    wget https://github.com/thewh1teagle/style-onnx/releases/download/model-files-v1.0/libritts_hebrew.onnx
    wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx

Transcribe models:
    wget https://huggingface.co/ivrit-ai/whisper-large-v3-turbo-ggml/resolve/main/ggml-model.bin

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


def main():
    print(BANNER)

    while True:
        key = wait_for_key()
        if key == "q":
            break

        path = record()
        if not path:
            print("No audio recorded.")
            continue

        print("Transcribing...")
        text = transcribe(path)
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
