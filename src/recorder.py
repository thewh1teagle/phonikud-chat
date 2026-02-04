import sys
import select
import termios
import threading
import time
import tempfile
import tty
import os

import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
HOLD_TIMEOUT = 0.5


def _pick_input_device():
    env_device = os.getenv("AUDIO_INPUT_DEVICE", "").strip()
    if env_device.isdigit():
        return int(env_device)

    default_input = sd.default.device[0]
    return default_input if default_input is not None and default_input >= 0 else None


def _open_input_stream(device, callback):
    env_rate = os.getenv("AUDIO_SAMPLE_RATE")
    dev = sd.query_devices(device, "input")
    candidates = []
    if env_rate and env_rate.isdigit():
        candidates.append(int(env_rate))
    if dev.get("default_samplerate"):
        candidates.append(int(round(dev["default_samplerate"])))
    candidates.extend([SAMPLE_RATE, 48000, 44100])

    seen = set()
    unique_rates = []
    for rate in candidates:
        if rate > 0 and rate not in seen:
            seen.add(rate)
            unique_rates.append(rate)

    last_error = None
    for rate in unique_rates:
        try:
            stream = sd.InputStream(
                samplerate=rate,
                channels=1,
                dtype="float32",
                callback=callback,
                device=device,
            )
            return stream, rate
        except Exception as err:
            last_error = err

    raise last_error


def _record_while_held(fd):
    """Record audio while R is held. Detects release via key-repeat timeout."""
    audio_frames = []
    stop_anim = threading.Event()

    def callback(indata, frames, time_info, status):
        audio_frames.append(indata.copy())

    def animate():
        states = ["Recording", "Recording.", "Recording..", "Recording..."]
        i = 0
        while not stop_anim.is_set():
            sys.stdout.write(f"\r  {states[i % len(states)]}   ")
            sys.stdout.flush()
            i += 1
            time.sleep(0.3)

    device = _pick_input_device()
    stream, sample_rate = _open_input_stream(device, callback)
    stream.start()
    threading.Thread(target=animate, daemon=True).start()

    while True:
        rlist, _, _ = select.select([sys.stdin], [], [], HOLD_TIMEOUT)
        if rlist:
            sys.stdin.read(1)
        else:
            break

    stop_anim.set()
    stream.stop()
    stream.close()

    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()

    return audio_frames, sample_rate


def wait_for_key():
    """Block until R or Q is pressed. Returns the key character."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1).lower()
            if ch in ("r", "q"):
                return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def record():
    """Hold R to record. Returns path to WAV file, or None if nothing captured."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        frames, sample_rate = _record_while_held(fd)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    if not frames:
        return None

    audio = np.concatenate(frames, axis=0)

    with tempfile.NamedTemporaryFile(suffix=".wav", prefix="phonikud_", delete=False) as tmp:
        path = tmp.name
    sf.write(path, audio, sample_rate)
    return path
