import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

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


def main():
    print("VoiceFlow macOS - Speech-to-Text")

    print("Loading Whisper model...")

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
    )

    audio = record_audio()
    transcribe_audio(model, audio)


if __name__ == "__main__":
    main()