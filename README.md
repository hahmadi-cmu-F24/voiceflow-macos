# VoiceFlow macOS 🎙️

A lightweight macOS speech-to-text dictation application built with Python and OpenAI's Whisper model.

VoiceFlow lets users record speech using a global keyboard shortcut, transcribe it locally, and automatically paste the resulting text into their active application.

Inspired by the workflow of tools like Wispr Flow, this project explores building a fast, convenient, system-wide dictation experience on macOS.

## Features

- **Local speech-to-text:** Uses Faster-Whisper for on-device transcription without sending recordings to a cloud transcription API.
- **Global keyboard shortcut:** Press `Control + Option + R` to start or stop recording.
- **Automatic text insertion:** Pastes transcribed text into the active application.
- **Clipboard preservation:** Temporarily uses the clipboard for pasting, then restores its previous plain-text contents.
- **macOS menu-bar interface:** Displays Ready, Recording, and Transcribing states.
- **Native permission checks:** Checks microphone and Accessibility permissions before starting.
- **Graceful shutdown:** Releases microphone resources when quitting through the menu bar.
- **Recording limit:** Automatically stops recording after 120 seconds.

## Tech Stack

- **Python 3**
- **Faster-Whisper:** Local speech recognition
- **SoundDevice / NumPy:** Microphone audio capture and processing
- **Pynput:** Global keyboard shortcuts and simulated keyboard input
- **Pyperclip:** Clipboard-based text insertion
- **Rumps:** macOS menu-bar interface
- **PyObjC:** Native macOS microphone and Accessibility permission checks

## Getting Started

### Requirements

- macOS
- Python 3.13 (development environment)
- A working microphone
- Microphone and Accessibility permissions

### Installation

Clone the repository:

```bash
git clone https://github.com/hahmadi-cmu-F24/voiceflow-macos.git
cd voiceflow-macos
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

### Run VoiceFlow

```bash
python3 main.py
```

On startup, VoiceFlow checks the required macOS permissions and loads the Whisper model. The first run may download the model files.

### How to Use

1. Launch VoiceFlow and wait for **🎙 Ready** in the menu bar.
2. Open a text editor, Notes, or another application where you want to enter text.
3. Place your cursor in the desired text field.
4. Press **Control + Option + R** to begin recording.
5. Speak naturally.
6. Press **Control + Option + R** again to stop.
7. Wait for transcription to finish. VoiceFlow automatically pastes the recognized text.

Use **Quit VoiceFlow** in the menu bar to close the application.

## macOS Permissions

VoiceFlow requires:

**Microphone access**  
System Settings → Privacy & Security → Microphone

**Accessibility access**  
System Settings → Privacy & Security → Accessibility

Grant access to the application running VoiceFlow, which may be Terminal, VS Code, or Python.

Depending on the macOS configuration, global shortcut functionality may also require Input Monitoring permission.

## Architecture

VoiceFlow separates the main functionality into several components:

| File | Responsibility |
|---|---|
| `main.py` | Application state, audio recording, transcription, and text insertion |
| `hotkey.py` | Global keyboard shortcut listener |
| `status_bar.py` | macOS menu-bar interface and status updates |
| `permissions.py` | Native microphone and Accessibility permission checks |

### Processing Flow

```text
Global Keyboard Shortcut
          |
          v
    Record Audio
          |
          v
   Stop Recording
          |
          v
  Background Worker
          |
          v
 Faster-Whisper Model
          |
          v
   Transcribed Text
          |
          v
   Clipboard + Paste
          |
          v
  Active Application
```

Audio is captured at 16 kHz and transcribed using Faster-Whisper's `base` model on the CPU with INT8 computation.

Transcription runs in a background thread so the application can maintain its menu-bar interface while processing audio.

## Current Limitations

VoiceFlow is currently a working Python prototype rather than a packaged macOS application.

- The application must be launched through Python.
- Transcription is currently configured for English.
- The Whisper model is fixed to `base`.
- Clipboard restoration preserves plain text, not all rich clipboard formats.
- Very quiet or silent recordings may produce inaccurate transcriptions.
- Terminal interruption with `Ctrl+C` may not follow the same cleanup path as the menu-bar Quit action.

## Future Improvements

Potential enhancements include:

- Configurable transcription languages and Whisper models
- Transcript preview and editing
- Improved silence detection
- More robust keyboard and permission handling
- Standalone macOS application packaging
- Additional performance and usability improvements

## Project Status

**Working prototype — actively being refined.**

The core recording, transcription, automatic pasting, menu-bar interface, and permission-checking workflows have been implemented and tested locally on macOS.

## Author

Hamzah Ahmadi

[GitHub](https://github.com/hahmadi-cmu-F24)