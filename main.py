import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import threading
import pyperclip

from hotkey import start_hotkey_listener
from pynput.keyboard import Controller, Key

# Audio configuration
SAMPLE_RATE = 16000
DURATION = 5  # seconds


def record_audio():
    """Record audio from the default microphone."""

    print(f"\nRecording for {DURATION} seconds. Speak now!")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )

    sd.wait()

    print("Recording complete!")

    return audio.flatten()


def transcribe_audio(model, audio):
    """Convert recorded speech into text using Whisper."""

    print("Transcribing...")

    start_time = time.perf_counter()

    segments, info = model.transcribe(
        audio,
        beam_size=5,
        language="en",
    )

    # Whisper returns segments lazily, so consume them
    # before measuring the completed transcription time.
    text = " ".join(
        segment.text.strip() for segment in segments
    )

    elapsed = time.perf_counter() - start_time

    print(f"\nTranscription: {text}")
    print(f"Transcription time: {elapsed:.2f} seconds")

    return text


keyboard_controller = Controller()
recording_lock = threading.Lock()


def dictate(model):
    """Record, transcribe, and paste into the active application."""

    if not recording_lock.acquire(blocking=False):
        print("Already recording or transcribing.")
        return

    try:
        audio = record_audio()
        text = transcribe_audio(model, audio)

        if text.strip():
            pyperclip.copy(text)

            # Paste the transcription using Cmd + V.
            with keyboard_controller.pressed(Key.cmd):
                keyboard_controller.press("v")
                keyboard_controller.release("v")

            print("Text pasted successfully!")

    except Exception as error:
        print(f"Dictation error: {error}")

    finally:
        recording_lock.release()


def main():
    print("VoiceFlow macOS - Speech-to-Text")
    print("Loading Whisper model...")

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
    )

    def on_hotkey():
        threading.Thread(
            target=dictate,
            args=(model,),
            daemon=True,
        ).start()

    start_hotkey_listener(on_hotkey)


if __name__ == "__main__":
    main()