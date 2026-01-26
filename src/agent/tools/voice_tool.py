from tts import set_voice

VOICES = {
    # Female
    "af_heart": "warm female, default, high quality",
    "af_bella": "confident female, high quality",
    "af_nicole": "soft whispery female",
    "af_aoede": "clear female",
    "af_kore": "calm female",
    "af_sarah": "friendly female",
    "af_alloy": "neutral female",
    "af_nova": "bright female",
    "af_sky": "light female",
    "af_jessica": "casual female",
    "af_river": "smooth female",
    # Male
    "am_fenrir": "deep strong male",
    "am_michael": "steady male",
    "am_puck": "playful male",
    "am_adam": "low male",
    "am_echo": "resonant male",
    "am_eric": "clear male",
    "am_liam": "young male",
    "am_onyx": "dark male",
    "am_santa": "jolly male",
}

SCHEMA = {
    "type": "function",
    "function": {
        "name": "set_voice",
        "description": (
            "Change the speaking voice for the next response. "
            "Use this when the user asks to change voice, tone, mood, or gender. "
            "Available voices: "
            + "; ".join(f"{k} ({v})" for k, v in VOICES.items())
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "voice": {
                    "type": "string",
                    "enum": list(VOICES.keys()),
                    "description": "The voice ID to use.",
                },
            },
            "required": ["voice"],
        },
    },
}


def execute(voice, **_):
    if voice not in VOICES:
        return f"Unknown voice '{voice}'. Available: {', '.join(VOICES.keys())}"
    set_voice(voice)
    return "Done."
