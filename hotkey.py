from pynput import keyboard


def start_hotkey_listener(on_activate):
    print("VoiceFlow is running.")
    print("Press Ctrl + Option + Space to record.")
    print("Press Ctrl + C in the terminal to quit.")

    try:
        with keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+<space>": on_activate
        }) as listener:
            listener.join()

    except KeyboardInterrupt:
        print("\nVoiceFlow stopped. Goodbye!")