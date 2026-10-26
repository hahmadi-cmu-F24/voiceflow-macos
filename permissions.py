import threading

from AVFoundation import AVCaptureDevice, AVMediaTypeAudio  # type: ignore[attr-defined]
from ApplicationServices import AXIsProcessTrusted  # type: ignore[attr-defined]

def check_microphone_access():
    """Check or request macOS microphone permission."""

    status = AVCaptureDevice.authorizationStatusForMediaType_(
        AVMediaTypeAudio
    )

    # 3 = Authorized
    if status == 3:
        print("Microphone access confirmed.")
        return True

    # 2 = Denied, 1 = Restricted
    if status in (1, 2):
        print("\n⚠️ MICROPHONE ACCESS DENIED")
        print(
            "Enable microphone access in:\n"
            "System Settings → Privacy & Security → Microphone"
        )
        return False

    # 0 = Not determined: request permission.
    if status == 0:
        print("Requesting microphone permission...")

        permission_event = threading.Event()
        result = {"granted": False}

        def permission_callback(granted):
            result["granted"] = bool(granted)
            permission_event.set()

        AVCaptureDevice.requestAccessForMediaType_completionHandler_(
            AVMediaTypeAudio,
            permission_callback,
        )

        if not permission_event.wait(timeout=30):
            print("Microphone permission request timed out.")
            return False

        if result["granted"]:
            print("Microphone access confirmed.")
            return True

        print("Microphone permission was denied.")
        return False

    print(f"Unexpected microphone authorization status: {status}")
    return False

def check_accessibility_access():
    """Check whether macOS has granted Accessibility access."""

    if AXIsProcessTrusted():
        print("Accessibility access confirmed.")
        return True

    print("\n⚠️ ACCESSIBILITY ACCESS REQUIRED")
    print(
        "Enable Accessibility access in:\n"
        "System Settings → Privacy & Security → Accessibility"
    )
    print(
        "Allow the application running VoiceFlow "
        "(Terminal, VS Code, or Python)."
    )

    return False