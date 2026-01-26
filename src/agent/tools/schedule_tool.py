import threading

import sounddevice as sd

from tts import create_audio

_reminders = {}
_next_id = 1
_lock = threading.Lock()
_audio_lock = threading.Lock()

SCHEDULE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "schedule_reminder",
        "description": (
            "Schedule a spoken reminder after a delay. "
            "The assistant will speak the message aloud when the time comes. "
            "Use this when the user asks to be reminded, notified, or wants something scheduled."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "minutes": {
                    "type": "number",
                    "description": "Delay in minutes. Use 0 if specifying seconds instead.",
                },
                "seconds": {
                    "type": "number",
                    "description": "Additional delay in seconds. Combined with minutes.",
                },
                "topic": {
                    "type": "string",
                    "description": "Short topic of the reminder, e.g. 'call mom', 'take a break', 'check oven'. Used for listing and cancelling.",
                },
            },
            "required": ["topic"],
        },
    },
}

LIST_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_reminders",
        "description": "List all active pending reminders. Use when the user asks what reminders are set or scheduled.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

CANCEL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "cancel_reminder",
        "description": (
            "Cancel scheduled reminders. "
            "Pass cancel_all=true to cancel everything, "
            "or pass keyword to cancel reminders matching that topic."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cancel_all": {
                    "type": "boolean",
                    "description": "Set true to cancel all reminders.",
                },
                "keyword": {
                    "type": "string",
                    "description": "Cancel reminders whose topic matches this keyword.",
                },
            },
            "required": [],
        },
    },
}


TASK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "schedule_task",
        "description": (
            "Schedule a task that runs through the AI with full tool access after a delay, then speaks the result. "
            "Use this when the user wants the assistant to do something later that requires thinking or tool use, "
            "e.g. 'in five minutes tell me what time it is', 'in one hour check my reminders and report back'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "minutes": {
                    "type": "number",
                    "description": "Delay in minutes. Use 0 if specifying seconds instead.",
                },
                "seconds": {
                    "type": "number",
                    "description": "Additional delay in seconds. Combined with minutes.",
                },
                "topic": {
                    "type": "string",
                    "description": "Short topic for listing and cancelling, e.g. 'tell the time', 'weather check'.",
                },
                "prompt": {
                    "type": "string",
                    "description": "A full INSTRUCTION including ALL user requirements: voice, message, actions. NEVER pass just the raw message. Always write it as a command. Examples: 'Use whisper voice and say: Jacob, you are the best.', 'Check what time it is and tell the user.', 'Use a deep male voice and say: Time to wake up!'",
                },
            },
            "required": ["prompt"],
        },
    },
}


def _speak(reminder_id, topic):
    with _lock:
        _reminders.pop(reminder_id, None)
    message = f"Hey! {topic}."
    print(f"\n[schedule] speaking: {message}")
    with _audio_lock:
        sd.stop()
        samples, sr = create_audio(message)
        sd.play(samples, sr)
        sd.wait()


_EXCLUDED_IN_TASK = {"schedule_reminder", "schedule_task", "list_reminders", "cancel_reminder"}

_TASK_SYSTEM = (
    "You are executing a scheduled task. "
    "You MUST use your tools. Call get_current_datetime for time. Call set_voice to change voice. "
    "NEVER guess information, always use tools. "
    "Your final response will be spoken aloud as audio. "
    "Output ONLY the words to speak. No meta text like 'Done' or 'Task completed'. "
    "NEVER use emojis. Write numbers as words. Only basic punctuation."
)


def _run_task(reminder_id, topic, prompt):
    with _lock:
        _reminders.pop(reminder_id, None)
    print(f"\n[schedule] running task: {topic}")
    from agent.ask import ask
    response = ask(
        prompt,
        exclude_tools=_EXCLUDED_IN_TASK,
        system_prompt=_TASK_SYSTEM,
    )
    print(f"[schedule] task result: {response}")
    with _audio_lock:
        sd.stop()
        samples, sr = create_audio(response)
        sd.play(samples, sr)
        sd.wait()


def _match(keyword, topic):
    """Match if any word from keyword appears in topic."""
    kw_words = set(keyword.lower().split())
    topic_lower = topic.lower()
    return any(w in topic_lower for w in kw_words)


def schedule_execute(topic, minutes=0, seconds=0, **_):
    global _next_id
    total = max(float(minutes) * 60 + float(seconds), 1)
    with _lock:
        rid = _next_id
        _next_id += 1
        timer = threading.Timer(total, _speak, args=[rid, topic])
        timer.daemon = True
        _reminders[rid] = {"timer": timer, "topic": topic}
        timer.start()
    parts = []
    m = int(total // 60)
    s = int(total % 60)
    if m:
        parts.append(f"{m}m")
    if s:
        parts.append(f"{s}s")
    print(f"[schedule] #{rid} reminder in {' '.join(parts)}: {topic}")
    return "Done."


def task_execute(prompt, topic=None, minutes=0, seconds=0, **_):
    topic = topic or prompt[:40]
    global _next_id
    total = max(float(minutes) * 60 + float(seconds), 1)
    with _lock:
        rid = _next_id
        _next_id += 1
        timer = threading.Timer(total, _run_task, args=[rid, topic, prompt])
        timer.daemon = True
        _reminders[rid] = {"timer": timer, "topic": topic, "is_task": True}
        timer.start()
    parts = []
    m = int(total // 60)
    s = int(total % 60)
    if m:
        parts.append(f"{m}m")
    if s:
        parts.append(f"{s}s")
    print(f"[schedule] #{rid} task in {' '.join(parts)}: {topic}")
    return "Done."


def list_execute(**_):
    with _lock:
        if not _reminders:
            return "No active reminders."
        lines = [
            f"#{rid}: {r['topic']} ({'task' if r.get('is_task') else 'reminder'})"
            for rid, r in _reminders.items()
        ]
    return "\n".join(lines)


def cancel_execute(cancel_all=False, keyword=None, **_):
    cancelled = []
    with _lock:
        if cancel_all:
            targets = list(_reminders.keys())
        elif keyword:
            targets = [rid for rid, r in _reminders.items() if _match(keyword, r["topic"])]
        else:
            targets = list(_reminders.keys())
        for rid in targets:
            r = _reminders.pop(rid)
            r["timer"].cancel()
            cancelled.append(f"#{rid}: {r['topic']}")
            print(f"[schedule] cancelled #{rid}: {r['topic']}")
    if not cancelled:
        return "No matching reminders found."
    return f"Cancelled {len(cancelled)} reminder(s)."
