import sys
import select
import termios
import threading
import time
import tty

import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
HOLD_TIMEOUT = 0.5


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

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback
    )
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

    return audio_frames


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
        frames = _record_while_held(fd)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    if not frames:
        return None

    audio = np.concatenate(frames, axis=0)
    path = "audio.wav"
    sf.write(path, audio, SAMPLE_RATE)
    return path
