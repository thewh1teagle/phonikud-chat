# Phonikud Chat

Hebrew voice assistant with local Sonara STT + local TTS + Ollama.

## Features

- Real-time voice conversation like ChatGPT voice mode
- Hold-to-talk interface
- Hebrew speech-to-text via Sonara (OpenAI-compatible API)
- Hebrew text-to-speech via StyleTTS2 + Phonikud
- LLM responses via Ollama with tool calling

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [Ollama](https://ollama.com)

## Setup

```bash
git clone https://github.com/thewh1teagle/phonikud-chat
cd phonikud-chat
```

See [src/main.py](src/main.py) for model download links.

## Sonara STT setup

In one terminal:

```bash
wget https://github.com/thewh1teagle/sonara/releases/download/v0.1.0/sonara-linux-arm64 -O sonara
chmod +x sonara
./sonara pull "https://huggingface.co/ivrit-ai/whisper-large-v3-turbo-ggml/resolve/main/ggml-model.bin?download=true"
./sonara serve ./ggml-model.bin
```

The app uses Sonara through the OpenAI client at `http://localhost:11531/v1`.

## Usage

In a second terminal:

```bash
uv run src/main.py
```

Hold **R** to record, release to get a response. Press **Q** to quit.
