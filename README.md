# Phonikud Chat

Fully offline Hebrew voice assistant.

## Features

- Fully local - no internet required after setup
- Real-time voice conversation like ChatGPT voice mode
- Hold-to-talk interface with live recording animation
- Hebrew speech-to-text via Whisper
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

## Usage

```bash
uv run src/main.py
```

Hold **R** to record, release to get a response. Press **Q** to quit.
