import threading
import time

import numpy as np
import pyperclip
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput.keyboard import Controller, Key

from hotkey import start_hotkey_listener


SAMPLE_RATE = 16000
MAX_RECORDING_SECONDS = 120

keyboard_controller = Controller()


def transcribe_audio(model, audio):
    """Convert recorded speech into text using Whisper."""
    print("Transcribing...")

    start_time = time.perf_counter()

    segments, _ = model.transcribe(
        audio,
        beam_size=5,
        language="en",
    )

    text = " ".join(
        segment.text.strip() for segment in segments
    ).strip()

    elapsed = time.perf_counter() - start_time

    print(f"\nTranscription: {text}")
    print(f"Transcription time: {elapsed:.2f} seconds")

    return text


class VoiceFlow:
    def __init__(self, model):
        self.model = model
        self.state = "idle"
        self.lock = threading.RLock()
        self.stream = None
        self.audio_chunks = []
        self.started_at = None
        self.timer = None

    def audio_callback(self, indata, frames, time_info, status):
        """Collect audio while the microphone is recording."""
        if status:
            print(f"Audio warning: {status}")

        # Copy because sounddevice reuses its audio buffers.
        with self.lock:
            if self.state == "recording":
                self.audio_chunks.append(indata.copy())

    def start_recording(self):
        """Begin recording until the shortcut is pressed again."""
        with self.lock:
            if self.state != "idle":
                return

            self.audio_chunks = []

            try:
                self.stream = sd.InputStream(
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype="float32",
                    callback=self.audio_callback,
                )

                self.stream.start()

                self.started_at = time.monotonic()
                self.state = "recording"

                self.timer = threading.Timer(
                    MAX_RECORDING_SECONDS,
                    self.stop_recording,
                )
                self.timer.daemon = True
                self.timer.start()

                print("\n🔴 RECORDING")
                print("Press Ctrl + Option + r again to stop.")

            except Exception as error:
                print(f"Microphone error: {error}")

                if self.stream is not None:
                    self.stream.close()

                self.stream = None
                self.state = "idle"

    def stop_recording(self):
        """Stop recording and begin transcription."""
        with self.lock:
            if self.state != "recording":
                return

            self.state = "transcribing"

            if self.timer is not None:
                self.timer.cancel()
                self.timer = None

            if self.started_at is None:
                duration = 0.0
            else:
                duration = time.monotonic() - self.started_at

            stream = self.stream

        print(f"\n⏹ Recording stopped ({duration:.1f} seconds)")

        # Process in a worker so the keyboard listener stays responsive.
        threading.Thread(
            target=self.process_recording,
            args=(stream,),
            daemon=True,
        ).start()

    def process_recording(self, stream):
        """Finish audio capture, transcribe, and paste."""
        try:
            stream.stop()
            stream.close()

            with self.lock:
                chunks = self.audio_chunks
                self.audio_chunks = []
                self.stream = None

            if not chunks:
                print("No audio was captured.")
                return

            audio = np.concatenate(chunks, axis=0).flatten()

            if len(audio) < SAMPLE_RATE // 4:
                print("Recording too short. Try again.")
                return

            print("🟡 TRANSCRIBING")

            text = transcribe_audio(self.model, audio)

            if text:
                pyperclip.copy(text)

                with keyboard_controller.pressed(Key.cmd):
                    keyboard_controller.press("v")
                    keyboard_controller.release("v")

                print("Text pasted successfully!")
            else:
                print("No speech detected.")

        except Exception as error:
            print(f"Dictation error: {error}")

        finally:
            with self.lock:
                self.state = "idle"

            print("\n🟢 READY — Press shortcut to record again.")

    def toggle_recording(self):
        """Handle the global keyboard shortcut."""
        with self.lock:
            current_state = self.state

        if current_state == "idle":
            self.start_recording()

        elif current_state == "recording":
            self.stop_recording()

        else:
            print("Please wait. Still transcribing...")


def main():
    print("VoiceFlow macOS - Speech-to-Text")
    print("Loading Whisper model...")

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
    )

    app = VoiceFlow(model)

    print("\n🟢 READY")
    start_hotkey_listener(app.toggle_recording)


if __name__ == "__main__":
    main()