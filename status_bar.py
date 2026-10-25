import rumps


class VoiceFlowStatusBar(rumps.App):
    """Display VoiceFlow's current state in the macOS menu bar."""

    def __init__(self, voiceflow):
        super().__init__(
            name="VoiceFlow",
            title="🎙 Ready",
            quit_button=None,
        )

        self.voiceflow = voiceflow
        self.last_state = None

        self.menu = [
            rumps.MenuItem("Ctrl + Option + R to record"),
            rumps.MenuItem("Quit VoiceFlow", callback=self.quit_app),
        ]

        # Check the application state every 0.2 seconds.
        # The timer runs through the macOS UI event loop.
        self.status_timer = rumps.Timer(self.update_status, 0.2)
        self.status_timer.start()

    def update_status(self, _):
        """Refresh the menu-bar indicator when the state changes."""

        with self.voiceflow.lock:
            current_state = self.voiceflow.state

        if current_state == self.last_state:
            return

        self.last_state = current_state

        if current_state == "idle":
            self.title = "🎙 Ready"

        elif current_state == "recording":
            self.title = "🔴 Recording"

        elif current_state == "transcribing":
            self.title = "⏳ Transcribing"

    def quit_app(self, _):
        """Close the menu-bar application."""
        rumps.quit_application()